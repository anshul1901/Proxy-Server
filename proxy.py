import sys
import os
import socket
import threading

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

        # Maintain list of clients
        self.__clients = {}

        while True:

            try:
                (clientSocket, client_address) = self.serverSocket.accept()
                print("Connection accepted from " + str(client_address))
            except:
                print("ERROR : Error in accepting Clients / Keyboard interrupt Caught")
                sys.exit(0)

            # Creating threads to handle mutiple connections simultaneously (bonus)
            # d = threading.Thread(name=self._getClientName(client_address),
            # target = self.proxy_thread, args=(clientSocket, client_address))
            # d.setDaemon(True)
            # d.start()

            try:
                request = conn.recv(config['MAX_REQUEST_LEN'])
            except:
                print("ERROR: Couldn't receive request from client")
                sys.exit(0)

            # parse the first line
            first_line = request.split('\n')[0]

            # get url
            url = first_line.split(' ')[1]

            http_pos = url.find("://") # find pos of ://
            if (http_pos==-1):
                temp = url
            else:
                temp = url[(http_pos+3):] # get the rest of url

            port_pos = temp.find(":") # find the port pos (if any)

            # find end of web server
            webserver_pos = temp.find("/")
            if webserver_pos == -1:
                webserver_pos = len(temp)

            webserver = ""
            port = -1
            if (port_pos==-1 or webserver_pos < port_pos):

                # default port
                port = 80
                webserver = temp[:webserver_pos]

            else: # specific port
                port = int((temp[(port_pos+1):])[:webserver_pos-port_pos-1])
                webserver = temp[:port_pos]

            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(config['CONNECTION_TIMEOUT'])
            s.connect((webserver, port))
            s.sendall(request)

            while True:
                # receive data from web server
                data = s.recv(config['MAX_REQUEST_LEN'])

                if (len(data) > 0):
                    conn.send(data) # send to browser/client
                else:
                    break

config = {
'HOST_NAME': '127.0.0.1',
'MAX_REQUEST_LEN': 12345,
'BIND_PORT': 12345,
'CONNECTION_TIMEOUT': 40
}
s = Server(config)
