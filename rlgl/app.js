
/**
 * Module dependencies.
 */

var express = require('express');
var routes = require('./routes');
var user = require('./routes/user');
var http = require('http');
var path = require('path');

var app = express();

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

  switch (param) {
    case 'red':
    case 'green':
    case 'off':
    case 'init':
    case 'off':
      child = exec('python ../changecolor.py ' + param,
        function (error, stdout, stderr) {
          console.log('stdout: ' + stdout);
          console.log('stderr: ' + stderr);
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
  var color = req.params.color;

  piface(color);

  res.writeHead(200, {'Content-Type': 'text/plain'});
  res.end('color: ' + color);
};


var buildbot = function (req, response) {
  // http://mobiletools.doubledowninteractive.com:8088/json/builders/Dev%20Continuous%20Builder?select=&select=slaves&as_text=1
  var options = {
    host: 'mobiletools.doubledowninteractive.com',
    port: 8088,
    path: '/json/builders/Dev%20Continuous%20Builder'
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
        response.end('building');
      } else {
        options.path += '/builds/-1';
        pageData = "";
        http.get(options, function (res) {
          res.on('data', function (chunk) {
            pageData += chunk;
          });
          res.on('end', function(){
            data = JSON.parse(pageData);
            if (data && data.text) {
              response.end(JSON.stringify(data.text));
            } else {
              repsonse.end('error');
            }
            
          });
        });
      }
    });
  }).on('error', function(e) {
    console.log("Got error: " + e.message);
    response.writeHead(200, {'Content-Type': 'text/plain'});
    response.end('error: ' + color);
  });
};

app.get('/', routes.index);
app.get('/off', off);
app.get('/init', init);

app.get('/light/:color', changeColor);

app.get('/buildbot', buildbot);

http.createServer(app).listen(app.get('port'), function(){
  console.log('Express server listening on port ' + app.get('port'));
});
