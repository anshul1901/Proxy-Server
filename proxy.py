import sys
import os
import socket
import threading
import time

class Server:
    def __init__(self, config):
        """Setting up the proxy server."""

        try:
            self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except:
            print("ERROR: Couldn't create socket")
            sys.exit(0)

        try:
            self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except:
            print("ERROR: Couldnt setup socket address for reusability")
            sys.exit(0)

        try:
            self.serverSocket.bind((config['HOST_NAME'], config['BIND_PORT']))
        except:
            print("ERROR: Couldn't bind socket with port")
            sys.exit(0)

        try:
            self.serverSocket.listen(10)
            print("Proxy server listening on port " + str(config['BIND_PORT']))
        except:
            print("ERROR: Couldn't get server to listen")
            sys.exit(0)

        while True:
            try:
                (conn, addr) = self.serverSocket.accept()
                try:
                    threading.Thread(target=self.request_handler,
                                     args = [conn, addr, config]).start()
                    print("Thread initialized")
                except:
                    print("ERROR: Failed to initialize thread")
                    sys.exit(0)
                print("Connection accepted from " + str(addr))
            except:
                print("ERROR : Error in accepting Clients / Keyboard interrupt Caught")
                sys.exit(0)

    def request_handler(self, conn, addr, config):
        try:
            client_req = conn.recv(config['MAX_REQUEST_LEN'])
        except:
            print("ERROR: Couldn't receive request from client")
            sys.exit(0)

        req = client_req.split("\n")
        url = req[0].split(" ")[1]
        host = req[1].split(":")[1][1:]
        port = int(req[1].split(":")[2])

        print ("Opening socket to end server at" + host + ":" + str(port))

        try:
            sock = socket.socket()
        except:
            print("ERROR: Failed to create socket to end server")
            sys.exit(0)

        try:
            sock.connect((host, port))
        except:
            print("ERROR: Failed to connect to end server")
            sys.exit(0)

        http_pos = url.find("://")
        if http_pos != -1:
            url = url[(http_pos + 3):]

        file_pos = url.find("/")
        url = url[file_pos:]

        req[0] = "GET " + url + " HTTP/1.1"

        new_request = ""
        for i in req:
            new_request += (i + "\r\n")

        print("Forwarding request to end server " + url)
        try:
            sock.send(new_request)
        except:
            print("ERROR: Failed to send request to end server")
            sys.exit(0)

        try:
            response = sock.recv(config['MAX_REQUEST_LEN'])
            print(response)
        except:
            print("ERROR: No response received from end server")
            sys.exit(0)

        try:
            conn.send(response)
            print("Forwarding response to client")
        except:
            print("ERROR: Failed to send response back to client")
            sys.exit(0)

        print("Recieving data from origin server and forwarding to client")
        while True:
            data = sock.recv(1024)
            conn.send(data)
            if not data:
                break

        print ("Closing connection to client")
        try:
            conn.close()
        except:
            print("ERROR: Couldn't close connection")
            sys.exit(0)

        print("Exiting thread")
        print("\n\n")
        sys.exit(0)

config = {
'HOST_NAME': '127.0.0.1',
'MAX_REQUEST_LEN': 99999,
'BIND_PORT': 12345,
'CONNECTION_TIMEOUT': 10
}

s = Server(config)
