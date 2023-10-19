import socket
import os
import platform
import threading
import time

# Handles responses and errors
def handleResponse(resp):
    status = int(resp.split()[1])
    if status == 200:
        print(resp)
    elif status == 400:
        print("400: Bad Request")
    elif status == 404:
        print("404: Not Found")
    elif status == 505:
        print("505: P2P-CI Version Not Supported")
    else:
        print("Unknown error occured.\n")

# LOOKUP - to find peers that have the specified RFC
def requestLookup(socket, host, port):
    rfcNumber = input("Enter an RFC number: ")
    rfcTitle = input("Enter the title of the RFC: ")
    msg = "LOOKUP RFC " + rfcNumber + " P2P-CI/1.0\n"
    msg = msg + "Host: " + host + "\n"
    msg = msg + "Port: " + str(port) + "\n"
    msg = msg + "Title: " + rfcTitle + "\n"
    socket.send(msg.encode())
    handleResponse(socket.recv(1024).decode())

# LIST ALL - to request the whole index of RFCs from the server
def requestList(socket, host, port):
    msg = "LIST ALL P2P-CI/1.0\n"
    msg = msg + "Host: " + host + "\n"
    msg = msg + "Port: " + str(port) + "\n"
    socket.send(msg.encode())
    handleResponse(socket.recv(1024).decode())

# ADD - to add a locally available RFC to the server’s index
def addRFC(socket, host, port):
    rfcNumber = input("Enter the RFC number: ")
    rfcTitle = input("Enter the title of the RFC: ")
    msg = "ADD RFC " + rfcNumber + " P2P-CI/1.0\n"
    msg = msg + "Host: " + host + "\n"
    msg = msg + "Port: " + str(port) + "\n"
    msg = msg + "Title: " + rfcTitle + "\n"
    socket.send(msg.encode())
    resp = socket.recv(1024).decode()
    handleResponse(resp)
    
# ADD - to add an RFC to the server’s index from a download
def addRFC2(socket, host, port, number, title):
    #rfcNumber = input("Enter the RFC number: ")
    #rfcTitle = input("Enter the title of the RFC: ")
    msg = "ADD RFC " + number + " P2P-CI/1.0\n"
    msg = msg + "Host: " + host + "\n"
    msg = msg + "Port: " + str(port) + "\n"
    msg = msg + "Title: " + title + "\n"
    socket.send(msg.encode())
    resp = socket.recv(1024).decode()
    handleResponse(resp)

# GET - Download RFC from a peer
def getRFC(sock, host, port):
    rfcNumber = input("Enter an RFC number: ")
    rfcTitle = input("Enter the title of the RFC: ")
    
    # Look up RFC with server
    msg = "LOOKUP RFC " + rfcNumber + " P2P-CI/1.0\n"
    msg = msg + "Host: " + host + "\n"
    msg = msg + "Port: " + str(port) + "\n"
    msg = msg + "Title: " + rfcTitle + "\n"
    sock.send(msg.encode())
    
    # Error handling added here
    resp = sock.recv(1024).decode()
    print(resp)
    status = int(resp.split()[1])
    if status == 200:   # 200: RFC can be downloaded from a Peer
        # Parse the peer's host, port, and the RFC's title from server LOOKUP response
        rfcHost = input("Enter the peer host name: ")#resp.split('\n')[1].split()[3]
        rfcPort = int(input("Enter the peer port: "))#resp.split('\n')[1].split()[-1]
        # Connect to the peer that has the RFC you want to download
        peerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #print("***\n" + rfcHost + "\n" + rfcPort + "\n***" )
        peerSocket.connect((rfcHost, int(rfcPort)))
        msg = "GET RFC " + rfcNumber + " P2P-CI/1.0\n"
        msg = msg + "Host: " + host + "\n"
        msg = msg + "OS: " + str(platform.system()) + " " + str(platform.release()) + "\n"
        # Request RFC from peer
        filename = str(rfcNumber) + ".txt"
        open(filename, "w+")
        peerSocket.send(msg.encode())
        resp = peerSocket.recv(1024).decode()
        #print(resp)
        status = int(resp.split()[1])
        if status == 200:
           # filename = str(rfcNumber) + ".txt"
            # Save RFC as a file
            with open(filename, "w+") as file:
                # This removes the first six lines of the response and then writes
                # whatever remains to the file (which is the actual RFC data itself)
                file.write('\n'.join(resp.split('\n')[6:]))
            # Tell user that the RFC was saved to their computer
            addRFC2(sock, socket.gethostname(), port, rfcNumber, rfcTitle)
            print("'" + rfcTitle + "' was saved to your computer as '" + filename + "'.")
        elif status == 400:
            print("400: Bad Request")
        elif status == 404:
            print("404: Not Found")
        elif status == 505:
            print("505: P2P-CI Version Not Supported")
        else:
            print("Unknown error occured.\n")
    elif status == 400:
        print("400: Bad Request")
    elif status == 404:
        print("404: Not Found")
    elif status == 505:
        print("505: P2P-CI Version Not Supported")
    else:
        print("Unknown error occured.\n")

# Function that listens for RFC requests from a peer
def rfcRequestListen(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((socket.gethostbyname(socket.gethostname()), port))
    sock.listen(1)
    while True:
        conn, addr = sock.accept() # Accepts the RFC request
        requestMsg = conn.recv(1024).decode()
        rfcNumber = requestMsg.split()[2]
        rfcRequestReply(conn, rfcNumber) # Send the socket and RFC number to the RFC request reply function
        #conn.close()

# Function used by rfcRequestListen to reply to RFC requests from peers
def rfcRequestReply(socket, rfcNumber):
    filename = str(rfcNumber) + ".txt"
    try:
        with open(filename, "r") as file:
            # Build the response string 'msg'
            msg = "P2P-CI/1.0 200 OK\n"
            # Add the Date attribute
            msg = msg + "Date: " + time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime()) + "\n"
            # Add the OS attribute
            msg = msg + "OS: " + str(platform.system()) + " " + str(platform.release()) + "\n"
            # Add the Last-Modified attribute
            absoluteFilePath = os.path.abspath(filename)
            lastModifiedTime = os.path.getmtime(absoluteFilePath)
            lastModifiedFormatted = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(lastModifiedTime))
            msg = msg + "Last-Modified: " + lastModifiedFormatted + "\n"
            # Add the Content-Length attribute
            msg = msg + "Content-Length: " + str(os.path.getsize(filename)) + "\n"
            # Add the Content-Type attribute
            msg = msg + "Content-Type: text/text\n" 
            # Add the File data
            msg = msg + file.read()
            # Send the response message to the peer that requested it
            socket.send(msg.encode())
    except IOError:
        # If the file cannot be found, send 404 Not Found status to the peer
        msg = "P2P-CI/1.0 404 Not Found\n"
        msg = msg + "Date: " + time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime()) + "\n"
        msg = msg + "OS: " + str(platform.system()) + " " + str(platform.release()) + "\n"
        msg = msg + "Content-Length: 0\n"
        msg = msg + "Content-Type: text/text\n"
        msg = msg + "\n" # No data for the file that was not found
        socket.send(msg.encode())

# HELP - Displays the function of each of the commands to the user
def helpUser():
    print("How to use commands:")
    print("- Enter 'GET' to download an RFC from a peer.")
    print("- Enter 'ADD' to add a locally available RFC to the server's index.")
    print("- Enter 'LIST' to request the whole index of RFCs from the server.")
    print("- Enter 'LOOKUP' to find peers that have the specified RFC.")
    print("- Enter 'EXIT' to terminate the program.\n")

def main():
    # Create the connection - IPv4, TCP
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #hostC = socket.gethostname()
    host = socket.gethostname()#input("What is my host name? -> ")
    port = 7734
    sock.connect((host, port))
    port = int(input("Enter a port number: "))
    # Send client info and RFCs to the server
    message = "JOIN P2P-CI/1.0\nHost: " + host + "\nPort: " + str(port)
    sock.sendall(message.encode())
    # Create a thread for listening to incoming RFC requests from peers
    thread = threading.Thread(target=rfcRequestListen, args=((port,)))
    # Start the thread
    thread.start()
    # Keep connection open until it leaves the system
    while True:
        # Prompt user to enter command indicating what the process wants to do
        userCommand = input("Enter a command (GET, ADD, LIST, LOOKUP, HELP, EXIT): ")
        # GET - download an RFC from a peer
        if userCommand.upper() == "GET":
            getRFC(sock, host, port)
        # ADD - to add a locally available RFC to the server’s index
        elif userCommand.upper() == "ADD":
            addRFC(sock, host, port)
        # LIST - to request the whole index of RFCs from the server
        elif userCommand.upper() == "LIST":
            requestList(sock, host, port)
        # LOOKUP - to find peers that have the specified RFC
        elif userCommand.upper() == "LOOKUP":
            requestLookup(sock, host, port)
        # HELP - Displays the function of each of the commands to the user
        elif userCommand.upper() == "HELP":
            helpUser()
        # EXIT - Terminates the process
        elif userCommand.upper() == "EXIT":      
            message = "EXIT P2P-CI/1.0\nHost: " + host + "\nPort: " + str(port)
            sock.send(message.encode())
            os._exit(0)
        # Invalid input
        else:
            print("Invalid command. Please try again.\n")
            
main()