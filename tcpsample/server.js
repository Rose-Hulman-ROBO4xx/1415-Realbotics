var net = require('net');

var server = net.createServer();

server.on('listening', function(){ console.log('Server running') });
server.on('close', function(){ console.log('Server stopping') });

server.on('connection', function(socket){
	socket.name = '[' + socket.remoteAddress + ':' + socket.remotePort + ']';
	console.log('Client connected from ' + socket.name);

	socket.on('data', function(data){
		console.log(socket.name + ': ' + data);
		socket.write(data);
	});

	socket.on('close', function(error){
		console.log('Client ' + socket.name + ' disconnected');
	});
});

server.listen(4040);
