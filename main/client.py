import socket
import select
import errno
import sys

HEADER_LENGTH=10
IP='127.0.0.1'
PORT=1234

my_username=input('Username: ')

# Create a socket
# socket.AF_INET(address family internet) -> address family, IPv4, some other possible are AF_INET6, AF_BLUETOOTH, AF_UNIX
# socket.SOCK_STREAM -> TCP, conection-based, socket.SOCK_DGRAM - UDP, connectionless, datagrams, socket.SOCK_RAW - raw IP packets
client_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP,PORT))

# Set connection to non-blocking state, so that the .recv() call won't block, and it it does it will return some exception which will be handled
client_socket.setblocking(False)

username=my_username.encode("utf-8")
username_header=f"{len(username):<{HEADER_LENGTH}}".encode('utf-8')
client_socket.send(username_header+username)
while True:
    # Wait for user to input a message
    message=input(f"{my_username} > ")
    mess=message
    # if mesasge is not empty send it
    if message:
        message=message.encode('utf-8')

        # message header
        message_header=f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
        client_socket.send(message_header+message)

        # open chatlogs file 
        file_object = open('chatlogs.log', 'a')

        # Append username: message to a new line at the end of file
        file_object.write(my_username+':    '+mess+'\n')
 
        # Close the file
        file_object.close()
    try:
     while True:
        #  receive things
        username_header = client_socket.recv(HEADER_LENGTH)
        if not len(username_header):
            print("connection closed by the server")
            sys.exit()

        # get the username
        username_length=int(username_header.decode('utf-8').strip())
        username= client_socket.recv(username_length).decode('utf-8')

        #get the message
        message_header = client_socket.recv(HEADER_LENGTH)
        message_length = int(message_header.decode('utf-8').strip())
        message = client_socket.recv(message_length).decode('utf-8')

        # print the output to screen
        print(f'{username} > {message}')

    except IOError as e:

        # This is normal on non blocking connections - when there are no incoming data, error is going to be raised
        # Some operating systems will indicate that using AGAIN, and some using WOULDBLOCK error code
        # We are going to check for both - if one of them - that's expected, means no incoming data, continue as normal
        # If we got different error code - something happened
        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
            print('Reading error: {}'.format(str(e)))
            sys.exit()

        # We just did not receive anything
        continue

    except Exception as e:

        # Any other exception - something happened, exit
        print(f'Reading error: '.format(str(e)))
        sys.exit()
