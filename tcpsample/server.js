var net = require('net');

var server = net.createServer();

server.on('listening', function(){ console.log('Server running') });
server.on('close', function(){ console.log('Server stopping') });

server.on('connection', function(socket){
	var name = '[' + socket.remoteAddress + ':' + socket.remotePort + ']';
	console.log('Client connected from ' + name);

	socket.on('data', function(data){
		console.log(name + ': ' + data);
		socket.write(data);
	});

	socket.on('close', function(error){
		console.log('Client ' + name + ' disconnected');
	});
});

server.listen(4040);
