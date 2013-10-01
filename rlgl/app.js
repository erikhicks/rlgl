
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
    case 'init':
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


var changeColor = function (req, res) {
  var color = req.params.color;

  piface(color);

  res.writeHead(200, {'Content-Type': 'text/plain'});
  res.end('color: ' + color);
};

app.get('/', routes.index);
app.get('/off', init);
app.get('/init', init);

app.get('/light/:color', changeColor);


http.createServer(app).listen(app.get('port'), function(){
  console.log('Express server listening on port ' + app.get('port'));
});
