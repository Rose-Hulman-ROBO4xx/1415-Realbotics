var app = require('http').createServer(handler)
var io = require('socket.io')(app);
var fs = require('fs');

app.listen(80);

function handler (req, res) {
  fs.readFile(__dirname + '/index.html',
  function (err, data) {
    if (err) {
      res.writeHead(500);
      return res.end('Error loading index.html');
    }

    res.writeHead(200);
    res.end(data);
  });
}

var processLine;

var readline = require('readline');
var rl = readline.createInterface({
	  input: process.stdin,
	  output: process.stdout
});

rl.on('line', function(line){
	    processLine(line);
});

io.on('connection', function (socket) {
  console.log('client connected');

  socket.emit('command', 'Hello, Zhi Li');

  socket.on('response', function (data) {
    console.log(data);
  });

  socket.on('disconnect', function (data) {
    console.log('client disconnected');
  });

  processLine = function(line) { socket.emit('command', 'do the thing! ' + line)};

});
