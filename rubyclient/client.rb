require 'socket'
require 'json'
require 'thread'

def connect(address = 'localhost', port = 3001, token = 'meow')
    conn = RealboticsConnection.new(address, port, token)
    conn.start
    return conn
end

class RealboticsConnection

    def initialize(address, port, token)
        @socket = RealboticsSocket.new(address, port)
        @callbacks = {}
        @callbacks_lock = Mutex.new
        @thread = nil
        @token = token
    end

    def register_callback(command, &block)
        @callbacks_lock.synchronize{
            @callbacks[command] = block
        }
    end

    def say(message)
        @socket.send({'type' => 'device_response', 'message' => message})
    end

    def start
        @Thread = Thread.new{ run }
        authenticate
    end

    private

    def authenticate
        @socket.send({'type' => 'authenticate', 'hardware_token' => @token })
        
        while true
            msg = @socket.recv
            if msg['type'] == 'authentication_success'
                return
            elsif msg['type'] == 'authentication_failure'
                raise 'realbotics authentication failed'
            end
        end
    end

    def run
        while true
            msg = @socket.recv
            command = msg['data']['commandData']

            callback = nil
            arguments = nil

            @callbacks_lock.synchronize{
                @callbacks.each{|key, value|
                    if key.class == ''.class && key == command
                        callback = value
                        break
                    elsif key.class = //.class && key =~ command
                        callback = value
                        arguments = key.match(command).captures
                        break
                    end
                }
            }
            
            if arguments
                callback.call *arguments
            elsif callback
                callback.call
            end

        end
    end
end

class RealboticsSocket

    def initialize(address, port)
        @state = :prefix
        @length_remaining = 0
        @message_so_far = ''
        @socket = TCPSocket.new(address, port)
        @received_messages = Queue.new
    end

    def send(msg)
        string = JSON.generate msg
        string = "#{string.length}##{string}"

    end

    def recv(msg)
        while @received_messages.empty?
            recv_data
        end

        return @received_messages.deq
    end

    private

    def recv_data
        data = @socket.recv_nonblock 1024
        data.chars.each{|char|
            res = handle_char char
            if res
                @received_messages.enq res
            end
        }
    end


    def handle_char(char)
        if @length_remaining == 0
            @state = :prefix
            @length_remaining = 0
            @message_so_far = ''
        end

        if @state == :prefix
            if char == '#'
                @state = :message
            else
                @length_remaining *= 10
                @length_remaining += char.to_i
            end
        else
            @message_so_far += char
            @length_remaining -= 1
        end

        if @length_remaining == 0
            return JSON.parse @message_so_far
        else
            return nil
        end
    end

end
