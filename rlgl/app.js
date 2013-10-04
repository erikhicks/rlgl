
/**
 * Module dependencies.
 */

var express = require('express');
var routes = require('./routes');
var user = require('./routes/user');
var http = require('http');
var path = require('path');

var app = express();

var BB_HOST = 'mobiletools.doubledowninteractive.com';
var BB_PORT = 8088;
var BB_BRANCH = '/json/builders/Dev%20Continuous%20Builder';
//var BB_BRANCH = '/json/builders/MStaging%20Full%20Builder';

// all environments
app.set('port', process.env.PORT || 3000);
app.set('views', __dirname + '/views');
app.set('view engine', 'jade');
app.use(express.favicon());
app.use(express.logger('dev'));
app.use(express.bodyParser());
app.use(express.methodOverride());
app.use(app.router);
app.use(express.static(path.join(__dirname, 'public')));

// development only
if ('development' == app.get('env')) {
  app.use(express.errorHandler());
}


var piface = function (param) {
  var exec = require('child_process').exec,
    child;

  switch (param.trim()) {
    case 'red':
    case 'green':
    case 'off':
    case 'init':
    case 'purple on':
    case 'purple off':
    case 'yellow off':
    case 'yellow on':
      child = exec('python ../changecolor.py ' + param,
        function (error, stdout, stderr) {
          //console.log('stdout: ' + stdout);
          //console.log('stderr: ' + stderr);
          if (error !== null) {
            console.log('exec error: ' + error);
          }
      });
      break;

    default:
      console.log('unknown command');
  }
};

var init = function (req, res) {
  piface('init');

  res.writeHead(200, {'Content-Type': 'text/plain'});
  res.end('init');
};

var off = function (req, res) {
  piface('off');

  res.writeHead(200, {'Content-Type': 'text/plain'});
  res.end('off');
};

var changeColor = function (req, res) {
  var color = req.params.color ? req.params.color : '';
  var state = req.params.state ? req.params.state : '';

  piface(color + ' ' + state);

  res.writeHead(200, {'Content-Type': 'text/plain'});
  res.end('color:' + color + ' state:' + state);
};


// Determine if the build is idle/building
var isBuildActive = function (cb) {
  // http://mobiletools.doubledowninteractive.com:8088/json/builders/Dev%20Continuous%20Builder?select=&select=slaves&as_text=1
  var options = {
    host: BB_HOST,
    port: BB_PORT,
    path: BB_BRANCH
  };

  http.get(options, function(res) {
    var pageData = "";
    res.setEncoding('utf8');
    res.on('data', function (chunk) {
      pageData += chunk;
    });

    res.on('end', function(){
      var data = JSON.parse(pageData);
      if (data && data.state === 'building') {
        cb(true);
      } else {
        cb(false);
      }
    });
  }).on('error', function(e) {
    console.log("Got error: " + e.message);
    cb(false);
  });
};


var isBuildSuccess = function (cb) {
  var options = {
    host: BB_HOST,
    port: BB_PORT,
    path: BB_BRANCH + '/builds/-1'
  };

  http.get(options, function(res) {
    var pageData = "";
    res.setEncoding('utf8');
    res.on('data', function (chunk) {
      pageData += chunk;
    });

    res.on('end', function(){
      data = JSON.parse(pageData);
      if (data && data.text) {
        console.log(JSON.stringify(data.text));
        cb(data);
      }
    });
  }).on('error', function(e) {
    console.log("Got error: " + e.message);
  });
};


var buildbot = function (req, res) {

  isBuildSuccess(function (data) {
    //turn on green if successful
    if(data.text[1] === 'successful') {
      piface('green');
    }

    //turn on red if failed
    if(data.text[0] === 'failed') {
      piface('red');
    }

		//turn on purple/? if interrupted
    if(data.text[0] === 'exception') {
      piface('purple on');
    } else {
      piface('purple off');
    }

  });

  isBuildActive(function (active) {
    //turn on/off yellow
    if (active) {
      piface('yellow on');
      console.log('active');
    } else {
      piface('yellow off'); //TODO turn yellow off
      console.log('idle');
    }
  });

  if (res) {
    res.writeHead(200, {'Content-Type': 'text/plain'});
    res.end('buildbot');
  }

};

app.get('/', routes.index);
app.get('/off', off);
app.get('/init', init);

app.get('/light/:color', changeColor);
app.get('/light/:color/:state', changeColor);

app.get('/buildbot', buildbot);

setInterval(buildbot, 5000);

http.createServer(app).listen(app.get('port'), function(){
  console.log('Express server listening on port ' + app.get('port'));
});
