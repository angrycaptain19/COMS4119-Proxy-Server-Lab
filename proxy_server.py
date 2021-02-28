from socket import *
import sys
import os
import time
from urllib.parse import urlparse
from datetime import datetime
CACHE_FOLDER = "cache"


def parse_if_modify(request):
    """
    assume request is decoded
    parse the if modified since date to the server
    example request:

        GET http://httpbin.org/get HTTP/1.1
        Host: httpbin.org
        User-Agent: curl/7.71.1
        Proxy-Connection: Keep-Alive
        accept: application/json
        If-Modified-Since: Sun, 28 Feb 2021 19:41:00 GMT
    return: for example, "Sun, 28 Feb 2021 19:41:00 GMT"
    """
    arr = request.split('\r')
    date = None
    for component in arr:
        if "If-Modified-Since" in component:
            print("catch an if-modified-since...")
            date = component.split(':', 1)[1].strip()
            print(repr(date))
    return date


def is_latest_version(cache_file, client_time):
    """
    assume cache_file exist
    target time is the time in if-modified-since
    if client_time < cached_time, then we believe client does NOT have the latest cache
    otherwise we believe that client has the latest version
    """
    if client_time is None:
        # not latest version
        return False
    client_date = datetime.strptime(client_time, '%a, %d %b %Y %H:%M:%S GMT')
    cache_date = None
    with open(cache_file) as cfile:
        for readline in cfile:
            if "date" in readline.lower():
                cache_time = readline.split(":", 1)[1].strip()
                cache_date = datetime.strptime(cache_time, '%a, %d %b %Y %H:%M:%S GMT')
                break
    if cache_date is None:
        print("ERROR: no date found")
    return client_date >= cache_date


if len(sys.argv) <= 1:
    print('Usage : "python ProxyServer.py server_ip"\n[server_ip : It is the IP Address Of Proxy Server')
    sys.exit(2)
# Create a server socket, bind it to a port and start listening
if not os.path.exists('cache'):
    os.makedirs('cache')

tcpSerSock = socket(AF_INET, SOCK_STREAM)
# Fill in start.
servPort = 8888
tcpSerSock.bind((sys.argv[1], servPort))
tcpSerSock.listen(5) # put 5 socket at most in the waiting backlog
# Fill in end.
try:
    while 1:
        # Strat receiving data from the client
        print('Ready to serve...')
        tcpCliSock, addr = tcpSerSock.accept()
        print('Received a connection from:', addr)
        message = tcpCliSock.recv(4096).decode()  # Fill in start. # Fill in end.
        print("Message from client: ", message)
        if_modified_date = parse_if_modify(message)
        print("if modified date is", if_modified_date)
        try:
            # Extract the filename from the given message
            # print("received a message: \n", message)
            print("message.split() is: ", message.split())
            request_type = message.split()[0]  # GET or POST
            filename = message.split()[1].partition("//")[2].replace('/', '.') # do not use / in the path
            print("cache file name is ", filename)
            save_file_path = os.path.join(CACHE_FOLDER, filename)
            fileExist = "false"
        except Exception as e:
            print("Message Error, please retry: ", str(e))
            continue
        if request_type == "POST":
            # make a post request
            print("Making a POST request.....")
            # if the request is POST, then just pass it too the server
            print("Create a socket on the proxyserver")
            c = socket(AF_INET, SOCK_STREAM)  # Fill in start. # Fill in end.
            parsed = urlparse(message.split()[1])
            remote_host = parsed.hostname
            print("remote host name:", remote_host)
            hostn = remote_host.replace("www.", "",
                                        1)
            try:
                # Connect to the socket to port 80
                # Fill in start.
                print("Connect to the socket to port 80...")
                c.connect((hostn, 80))
                c.sendall(message.encode())
                time.sleep(0.05)  # sleep for 50 miliseconds
                data = c.recv(4096)
                print(data)
                tcpCliSock.sendall(data)  # just send back the data
            except gaierror as e:
                print("Hostname doesn't have IP Address" + hostn)
                print("reason: ", str(e))
                tcpCliSock.send("HTTP/1.1 404 Not Found\r\n".encode())
                tcpCliSock.send("\r\n".encode())
                tcpCliSock.send("\r\n".encode())

            except ConnectionRefusedError as e:
                print("Invalid Hostname" + hostn)
                print("reason: ", str(e))
                tcpCliSock.send("HTTP/1.1 404 Not Found\r\n".encode())
                tcpCliSock.send("\r\n".encode())
                tcpCliSock.send("\r\n".encode())
            continue

        # Then, it is GET request
        print("Making a GET request.....")
        try:
            # Check wether the file exist in the cache
            with open(save_file_path, 'r') as f:
                is_latest = is_latest_version(save_file_path, if_modified_date)
                if is_latest:
                    print("Client has the latest version!")
                    tcpCliSock.send("HTTP/1.1 304 Not Modified\r\n".encode())
                    # tcpCliSock.send("Content-Type:text/html\r\n".encode())
                else:
                    print("Client DOES NOT have the latest version!")
                    outputdata = f.readlines()
                    fileExist = "true"
                    tcpCliSock.send("HTTP/1.1 200 OK\r\n".encode())
                    tcpCliSock.send("Content-Type:text/html\r\n".encode())
                    # Fill in start.
                    for line in outputdata:
                        tcpCliSock.send(line.encode())
                    # Fill in end.
                    print('Read from cache')
        # Error handling for file not found in cache
        except IOError:
            if fileExist == "false":
                print("Create a socket on the proxyserver")
                c = socket(AF_INET, SOCK_STREAM) # Fill in start. # Fill in end.
                parsed = urlparse(message.split()[1])
                remote_host = parsed.hostname
                print("remote host name:", remote_host)
                hostn = remote_host.replace("www.","",1) # filename.replace("www.","",1).split('/')[0] # "gaia.cs.umass.edu" #  # message.split()[1].partition("//")[2].partition("/")[0]

                try:
                    # Connect to the socket to port 80
                    # Fill in start.
                    print("Connect to the socket to port 80...")
                    c.connect((hostn, 80))
                    c.sendall(message.encode())
                    time.sleep(0.05)  # sleep for 50 miliseconds
                    data = c.recv(4096)
                    print(data)
                    tcpCliSock.sendall(data)  # just send back the data
                    tmpFile = open(save_file_path, "wb")
                    tmpFile.write(data) # .decode().replace('\r\n', '\n')
                    print("save to file path, ", save_file_path)
                    tmpFile.close()
                    # Fill in end.
                except gaierror as e:
                    print("Hostname doesn't have IP Address" + hostn)
                    print("reason: ", str(e))
                    tcpCliSock.send("HTTP/1.1 404 Not Found\r\n".encode())
                    tcpCliSock.send("\r\n".encode())
                    tcpCliSock.send("\r\n".encode())

                except ConnectionRefusedError as e:
                    print("Invalid Hostname" + hostn)
                    print("reason: ", str(e))
                    tcpCliSock.send("HTTP/1.1 404 Not Found\r\n".encode())
                    tcpCliSock.send("\r\n".encode())
                    tcpCliSock.send("\r\n".encode())
                # except Exception as e:
                #     print("Illegal request, reason: ", str(e))
                #     # break
            else:
                tcpCliSock.send("HTTP/1.1 404 Not Found\r\n".encode())
                tcpCliSock.send("\r\n".encode())
                tcpCliSock.send("\r\n".encode())
        # Close the client and the server sockets
        tcpCliSock.close()
except KeyboardInterrupt:
    # good habit to close the socket for client
    # Fill in start.
    print("key board interrupt to close connection.....")
    tcpSerSock.close()
    # Fill in end.
