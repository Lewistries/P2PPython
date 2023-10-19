import collections
import socket
import threading
import os

peers = collections.deque([])
RFC_Index = collections.deque([])

#Classes to hold Peer and RFC information and response types
############################################################
class Responses:
    #200 OK
    #400 Bad Request
    #404 Not Found
    #505 P2P-CI Version Not Supported
    def Okay():
        return "P2P-CI/1.0 200 OK"
    def Bad_Request():
        return "P2P-CI/1.0 400 Bad Request\n"
    def Not_Found():
        return "P2P-CI/1.0 404 Not Found\n"
    def Not_Supported():
        return "P2P-CI/1.0 505 P2P-CI Version Not Supported\n"
    

class Peer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        
class RFC:
    def __init__(self, RFC_num, RFC_title, RFC_hostname, RFC_port):
        self.number = RFC_num
        self.title = RFC_title
        self.hostname = RFC_hostname
        self.port = RFC_port
#End
##############################################################        
#Main server Functionality code

def join(data):
    #print(data)
    peers.appendleft(Peer(data[1].split(':')[1].strip(), data[2].split(':')[1].strip()))
    #print(data[1].split(':')[1].strip())

def add(data, sock):
    
    port_num = data[2].split(' ')[1].strip()
    RFC_num = data[0].split(' ')[2].strip()
    RFC_title = data[3].split(':')[1].strip()
    RFC_host = data[1].split(':')[1].strip()
    #print(data)
    r = False
    for element in RFC_Index:
        if(element.number == RFC_num and RFC_host == element.hostname and port_num == element.port):
            message = Responses.Bad_Request()
            r = True
    if (not r):
        RFC_Index.appendleft(RFC(RFC_num, RFC_title, RFC_host, port_num))
        message = Responses.Okay() + "\nRFC " + RFC_num + " " + RFC_title + " " + RFC_host + " " + port_num
    sock.send(message.encode())
    
def lookUp(data, sock):
    #LOOKUP RFC 3457 P2P-CI/1.0
    #Host: thishost.csc.ncsu.edu
    #Port: 5678
    #Title: Requirements for IPsec Remote Access Scenarios
    message = Responses.Okay()
    RFC_num = data[0].split(' ')[2].strip()
    port_num = data[2].split(' ')[1].strip()
    RFC_title = data[3].split(':')[1].strip()
    found = False
    count = 0
    for element in RFC_Index:
        if(element.number == RFC_num):
            found = True
            if(element.title == RFC_title):
                count = count + 1
                message += "\nRFC " + RFC_num + " " + element.title + " " + element.hostname + " " + element.port
    if(found and count > 0):
        sock.send(message.encode())
    elif(found):
        sock.send(Responses.Bad_Request().encode())
    else:
        sock.send(Responses.Not_Found().encode())
    

def list(data, sock):
    message = Responses.Okay()
    port_num = data[2].split(' ')[1].strip()
    for element in RFC_Index:
        message += "\nRFC " + element.number + " " + element.title + " " + element.hostname + " " + element.port
    sock.send(message.encode())
    

def exitServer(data):
    global RFC_Index
    global peers
    host_name = data[1].split(':')[1].strip()
    host_port = data[2].split(':')[1].strip()
    #print(host_name)
    new_RFC = RFC_Index.copy()
    new_peers = peers.copy()
    for elements in new_RFC:
        #print(elements.hostname)
        if(elements.hostname == host_name and elements.port == host_port):
            RFC_Index.remove(elements)
    for peer in new_peers:
        #print(peer.host)
        if(peer.host == host_name and peer.port == host_port):
            peers.remove(peer)
            break
    


def handle_request(new_connection):
    while True:
        request = new_connection.recv(1024).decode()
        #print(request)
        data = request.split('\n')
    
        case = data[0].split(' ')[0].strip()
        if(case == "JOIN"):
            join(data)
        elif(case == "ADD"):
            add(data, new_connection)
        elif(case == "LOOKUP"):
            lookUp(data, new_connection)
        elif(case == "LIST"):
            list(data, new_connection)
        elif(case == "EXIT"):
            exitServer(data)
            return
        else:
            new_connection.send(Responses.Bad_Request().encode())
   # match(data.split(' ')[0]):
    #    case 'JOIN':
     #       join(data)
     #   case 'ADD':
     #     add(data, new_connection)
      #  case 'LOOKUP':
      #      lookUp(data, new_connection)
      #  case 'LIST':
      #      list(data, new_connection)
      #  case 'EXIT':
      #      exit(data)
      ##  case _:
       #     new_connection.send(Responses.Bad_Request().encode())
    
        
def main():
    
    connector = socket.socket()
    
    host = socket.gethostname()
    #print(host)
    port = 7734
    
    connector.bind((host, port))
    connector.listen()
    while(True):
        #print("I get here\n")
        new_con = connector.accept()[0]
        
        threading.Thread(target=handle_request,args=(new_con,)).start()
        #if(os.fork() == 0):
           # connector.close()
           # handle_request(new_con)
           # exit(0)
        
        #new_connection.close()
        
main()