var http = require('http');

http.createServer( function(req,res) {

   var currentTime = new Date();
   console.log('Client called at '+currentTime);

   res.writeHead(200, {'Content-Type':'text/plain'});
   res.write('RLGL\n');
   res.end();

}).listen('8124', function () {
   console.log('listening on port 8124');
});
