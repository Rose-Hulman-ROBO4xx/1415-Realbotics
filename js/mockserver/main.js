var app = require('http').createServer(handler)
var io = require('socket.io')(app);

app.listen(1080);

function handler (req, res) {
	res.writeHead(200);
	res.end('ok');
}

io.on('connection', function (socket) {
  socket.emit('news', { text: 'Hello, world!'});
});
