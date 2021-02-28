# http://gaia.cs.umass.edu/wireshark-labs/HTTP-wireshark-file2.html
# http://gaia.cs.umass.edu/wireshark-labs/HTTP-wireshark-file1.html

from socket import *
import sys
import time
if len(sys.argv) <= 1:
    print('Usage : "python ProxyServer.py server_ip"\n[server_ip : It is the IP Address Of Proxy Server')
    sys.exit(2)
# Create a server socket, bind it to a port and start listening
tcpSerSock = socket(AF_INET, SOCK_STREAM)
# Fill in start.
servPort = 8080
# sys.argv[1]
tcpSerSock.bind((sys.argv[1], servPort))
tcpSerSock.listen(5) # put 5 socket at most in the waiting backlog
# Fill in end.
while 1:
    # Strat receiving data from the client
    print('Ready to serve...')
    tcpCliSock, addr = tcpSerSock.accept()
    print('Received a connection from:', addr)
    time.sleep(0.5)
    message = tcpCliSock.recv(4096).decode()  # Fill in start. # Fill in end.
    # print(message)
    # message = message.decode()
    print("From client: ", message)
    # Extract the filename from the given message
    print(message.split()[1])
    filename = message.split()[1].partition("/")[2]# .replace('/', '_')
    print(filename)
    fileExist = "false"
    filetouse = "/" + filename
    print(filetouse)
    try:
        # Check wether the file exist in the cache
        f = open(filetouse[1:], "r")
        outputdata = f.readlines()
        fileExist = "true"
        # ProxyServer finds a cache hit and generates a response message
        tcpCliSock.send("HTTP/1.0 200 OK\r\n".encode())
        tcpCliSock.send("Content-Type:text/html\r\n".encode())
        # Fill in start.
        for line in outputdata:
            tcpCliSock.send(line.encode())
        # Fill in end.
        # maybe there is an indent?
        print('Read from cache')
    # Error handling for file not found in cache
    except IOError:
        if fileExist == "false":
            print("Create a socket on the proxyserver")
            c = socket(AF_INET, SOCK_STREAM) # Fill in start. # Fill in end.
            hostn = filename.replace("www.","",1).split('/')[0] # "gaia.cs.umass.edu" #  # message.split()[1].partition("//")[2].partition("/")[0]
            print("host name:", hostn)
            try:
                # Connect to the socket to port 80
                # Fill in start.
                print("Connect to the socket to port 80...")
                c.connect((hostn, 80))
                c.sendall(message.encode())
                time.sleep(0.05)  # sleep for 50 miliseconds
                data = c.recv(4096)
                print(data)
                # Fill in end.
                # Create a temporary file on this socket and ask port 80 for the file requested by the client
                # fileobj = c.makefile('r', 0)
                # fileobj.write("GET "+"http://" + filename + "HTTP/1.0\n\n")
                # Read the response into buffer
                # Fill in start.
                tcpCliSock.sendall(data)  # just send back the data
                # Fill in end.
                # Create a new file in the cache for the requested file.
                # Also send the response in the buffer to client socket and the corresponding file in the cache
                # tmpFile = open("./" + filename,"wb") # Fill in start.
                # tmpFile = open("./" + filename, "wb")
                #
                # tmpFile.writelines(data) # .decode().replace('\r\n', '\n')
                # tmpFile.close()
                # Fill in end.
            except Exception as e:
                print(str(e))
                print("Illegal request")
        else:
            # HTTP response message for file not found # Fill in start.
            # Fill in end.
            pass
    # Close the client and the server sockets
    tcpCliSock.close()
# Fill in start.
# Fill in end.