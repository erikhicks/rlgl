import sys
import argparse
import glob
import datetime
import hashlib
import hmac
import socket
import requests
import json


DEBUG=False

DNSME_API_KEY='d531ff2b-495b-4a21-b0cb-4a2ffadfbd31'
DNSME_SECRET_KEY='8579b318-baaa-47a2-b676-4eb026c71439'

API_KEY_HEADER='x-dnsme-apiKey'
REQUEST_DATE_HEADER='x-dnsme-requestDate'
HMAC_HASH_HEADER='x-dnsme-hmac'

domainName=None
domainId=None
lastResponse=None


def formattedDatestring():
    # make a datestring like 'Mon, 12 Nov 2012 23:20:25 GMT'
    t = datetime.datetime.utcnow()
    formattedDate = t.strftime("%a, %d %b %Y %H:%M:%S GMT")
    return formattedDate

def hmacHashFromDate(formattedDate):
    hmacHash=hmac.new(DNSME_SECRET_KEY, formattedDate, hashlib.sha1)
    return hmacHash.hexdigest()

def addApiKeyHeader(headers):
    headers[API_KEY_HEADER]=DNSME_API_KEY
    return headers
    
def addRequestDateHeader(headers,fmtDatestring):
    headers[REQUEST_DATE_HEADER]=fmtDatestring
    return headers
    
def addHMACHashHeader(headers,hmacHash):
    headers[HMAC_HASH_HEADER]=hmacHash
    return headers

def makeHttpHeaders(fmtDatestring=None, hmacHash=None):
    if fmtDatestring == None:
        fmtDatestring = formattedDatestring()
    if hmacHash == None:
        hmacHash = hmacHashFromDate(fmtDatestring)
    # build headers
    httpHeaders = {}
    httpHeaders = addApiKeyHeader(httpHeaders)
    httpHeaders = addRequestDateHeader(httpHeaders, fmtDatestring)
    httpHeaders = addHMACHashHeader(httpHeaders, hmacHash)
    
    httpHeaders['content-type'] = 'application/json'
    httpHeaders['accept'] = 'application/json'
    # print 'httpHeaders =',httpHeaders
    return httpHeaders

# open URL 

def buildAndSendRequest(url, params, httpHeaders,requestType='GET'):
    global DEBUG
    global lastResponse
    data=None
    if requestType == 'DELETE':
        requestFunc = requests.delete
        r = requestFunc(url, headers=httpHeaders, params=params)
    elif requestType == 'PUT':
        requestFunc = requests.put
        data=json.dumps(params)
        params=None
        r = requestFunc(url, headers=httpHeaders, data=data)
    elif requestType == 'POST':
        requestFunc = requests.post
        data=json.dumps(params)
        params=None
        r = requestFunc(url, headers=httpHeaders, data=data)
    else:
        requestFunc = requests.get
        r = requestFunc(url, headers=httpHeaders, params=params)
        
    if DEBUG:
        print "buildAndSendRequest:"
        print "url =",url
        print "requestType =",requestType
        print "headers =",httpHeaders
        print "params =",params
        print "data =",data
        print "requestFunc =",requestFunc
        print
    lastResponse = r
    print "Response r=",r
    print 'converting response to json'
    responseData = r.json()
    print 'done converting'
    return responseData

def sendRequestWithParams(url, params=None, requestType='GET'):
    print 'sending request with params'
    # first set datestring and hash
    fmtDatestring = formattedDatestring()
    # print 'datestring =',fmtDatestring
    hmacHash = hmacHashFromDate(fmtDatestring)
    # print 'hash =',hmacHash
    # build headers
    httpHeaders = makeHttpHeaders(fmtDatestring, hmacHash)
    responseData = buildAndSendRequest(url, params, httpHeaders, requestType)
    print 'done sending request, returning response data'
    print responseData
    return responseData
    
def sendRequest_dnsManaged():
    url='https://api.dnsmadeeasy.com/V2.0/dns/managed'
    responseData = sendRequestWithParams(url)
    return responseData
    
def getDomainData(domainName):
    jsonData = sendRequest_dnsManaged()
    dataList = jsonData['data']
    data = None
    for d in dataList:
        if d['name'] == domainName:
            data = d
            break
    return data
    
def getDomainId(domainName):
    domainJson = getDomainData(domainName)
    id = domainJson['id']
    return id
    
def getDomainRecords(domainName):
    id = getDomainId(domainName)
    url='https://api.dnsmadeeasy.com/V2.0/dns/managed/'+str(id)+'/records'
    responseData = sendRequestWithParams(url)
    return responseData
    
def getDNSRecordMatchingFields(domainName, matchDict):
    print 'getting DNS record for matcing fields'
    jsonData = getDomainRecords(domainName)
    dataList = jsonData['data']
    data = None
    keys = matchDict.keys()
    for d in dataList:
        for k in keys:
            match = True
            if k in d:
                if d[k] != matchDict[k]:
                    match = False
                    break
        if match:
            data = d
            break
    print 'done getting dns record'
    return data
    
def getDNSRecordForHostAndDomain(host, domainName, type='A'):
    matchDict = {}
    matchDict['name'] = host
    matchDict['type'] = type    
    return getDNSRecordMatchingFields(domainName, matchDict)

def deleteDomainARecord(host, domainName):
    record = getDNSRecordForHostAndDomain(host, domainName)
    print "record =",record
    domainId = getDomainId(domainName)
    recordId = record['id']
    url='https://api.dnsmadeeasy.com/V2.0/dns/managed/'+str(domainId)+'/records/'+str(recordId)
    print "new record =",record
    responseData = sendRequestWithParams(url, None, 'DELETE')
    return record

def insertDomainRecord(domainName, valueDict):    
    domainId = getDomainId(domainName)
    url='https://api.dnsmadeeasy.com/V2.0/dns/managed/'+str(domainId)+'/records'
    responseData = sendRequestWithParams(url, valueDict, 'POST')
    return responseData

#    valueDict = {"name":'foo',"value":'10.0.1.1',"type":"A","ttl":1800,"gtdLocation":"DEFAULT"}
#    valueDict = {"name":'foo',"value":'10.0.1.1',"type":"A","ttl":1800,"gtdLocation":"DEFAULT"}

def createDomainARecord(hostname, domainName, ip):
    valueDict = {"name":hostname,"value":ip,"type":"A","ttl":1800,"gtdLocation":"DEFAULT"}
    responseData = insertDomainRecord(domainName, valueDict)
    return responseData

def replaceDomainRecord(host, domainName, valueDict):    
    record = getDNSRecordForHostAndDomain(host, domainName)
    print "record =",record
    domainId = getDomainId(domainName)
    recordId = record['id']
    deleteDomainARecord(host, domainName)
    url='https://api.dnsmadeeasy.com/V2.0/dns/managed/'+str(domainId)+'/records'
    del record['id']
    record['value'] = '1.2.3.4'
    print "new record =",record
    return insertDomainRecord('jjc-macmini2','iwantmy.mobi', record)    

# result = dnsme.createDomainARecord('foo', 'iwantmy.mobi','10.0.1.11')

def setValuesForDomainRecord(host, domainName, valueDict):
    print 'setting values for domain record'
    record = getDNSRecordForHostAndDomain(host, domainName)
    print "record =",record
    domainId = getDomainId(domainName)
    recordId = record['id']
    if not 'id' in valueDict.keys():
        valueDict['id'] = recordId
    url='https://api.dnsmadeeasy.com/V2.0/dns/managed/'+str(domainId)+'/records/'+str(recordId)
    responseData = sendRequestWithParams(url, valueDict, 'PUT')
    return responseData

def setIPAddressForDomainRecord(host, domainName, ipAddr):
    valueDict = {"name":host,"value":ipAddr,"type":"A","ttl":1800,"gtdLocation":"DEFAULT"}
    response = setValuesForDomainRecord(host, domainName, valueDict)    
    return response
    
def makeCurlCommand(url, params=None):
    # first set datestring and hash
    fmtDatestring = formattedDatestring()
    # print 'datestring =',fmtDatestring
    hmacHash = hmacHashFromDate(fmtDatestring)
    # print 'hash =',hmacHash
    # build headers
    httpHeaders = makeHttpHeaders(fmtDatestring, hmacHash)
    cmd="curl -v"
    print 'headers:'
    for h in httpHeaders:
        header=' -H "'+h+httpHeaders[h]+'" '
        cmd=cmd+header
    cmd=cmd+url
    print cmd
    # responseData = buildAndSendRequest(url, params, httpHeaders)


def main():
    parser = argparse.ArgumentParser(description='A command-line utilities for using the DNSMadeEasy REST API', epilog="commands are getdomainrecords, gethostrecord, addhost, removehost, setip")

    parser.add_argument('--host', action='store', help='the hostname')
    parser.add_argument('--domain', action='store', help='the domain name')
    parser.add_argument('cmd', action='store', help='the command to perform')
    parser.add_argument('cmdargs', action='store', nargs='?')

    args = parser.parse_args()

    # init return code to 0 (non-error)
    # in most cases we replace this with the return value of the
    # called function, except for things like runFixStyles where
    # we don't care about the return value
    retVal=0

    if args.cmd == 'setip':
        # cmdargs should be the ip address
        print 'we are setting an ip'
	if args.host != None and args.domain != None:
            result = setIPAddressForDomainRecord(args.host, args.domain, args.cmdargs)    
            print 'about to print result'
	    print result
	    print 'done'      
    elif args.cmd == 'removehost':
        # no cmd arg is needed
        if args.host != None and args.domain != None:
            result = deleteDomainARecord(args.host, args.domain)    
            print json.dumps(result)      
    elif args.cmd == 'addhost':
        # cmdargs should be the ip address
        print 'we are adding a host'
	if args.host != None and args.domain != None:
            result = createDomainARecord(args.host, args.domain, args.cmdargs)  
	    print result
    elif args.cmd == 'gethostrecord':
        # no cmdargs needed
        if args.host != None and args.domain != None:
            result = getDNSRecordForHostAndDomain(args.host, args.domain)   
            print json.dumps(result)     
    elif args.cmd == 'getdomainrecords':
        # no cmdargs needed, and no host needed
        if args.domain != None:
            result = getDomainRecords(args.domain)    
            print json.dumps(result)    
    return 0

if __name__ == '__main__':
    try:
        retVal=main()
        sys.exit(retVal)
    except Exception as err:
        print err
        sys.exit(1)
