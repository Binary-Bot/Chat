import time
from socket import *
import threading


def chatServer():
    serverSocket = socket()
    IP = getIPAddress()
    serverSocket.bind((IP, 2028))
    print("Listening on ", IP)
    serverSocket.listen()
    socketRooms = {}
    chatRooms = {}
    while True:
        try:
            clientSocket, addr = serverSocket.accept()
            threading.Thread(target=processRequest, args=(clientSocket, socketRooms, chatRooms)).start()
        except:
            print("Client disconnected")


def processRequest(clientSocket, socketRooms, chatRooms):
    msg = getMessage(clientSocket)
    while True:
        if msg[:4] == "JOIN":
            chatRoomName, UserName = joinRoom(msg, clientSocket, chatRooms, socketRooms)
            if not clientSocket._closed:
                while True:
                    msg = getMessage(clientSocket)
                    if msg[:4] == "SEND":
                        response = msg[5:]
                        if len(response) > 250:
                            response = "Maximum characters exceeded."
                            sendMessage(clientSocket, response)
                        else:
                            response = 'SENT' + "\t" + UserName + "\t" + response
                            for clients in socketRooms[chatRoomName]:
                                sendMessage(clients, response)

                    elif msg[:3] == "WHO":
                        response = chatRooms[chatRoomName]
                        response = "MEMBERS\t" + str(response)
                        sendMessage(clientSocket, response)

                    elif msg[:4] == "EXIT":
                        response = "LEFT\t" + UserName
                        for clients in socketRooms[chatRoomName]:
                            if clients == clientSocket:
                                socketRooms[chatRoomName].remove(clients)
                                sendMessage(clients, response)
                            else:
                                sendMessage(clients, response)
                        for users in chatRooms[chatRoomName]:
                            if users == UserName:
                                chatRooms[chatRoomName].remove(UserName)
                        if len(chatRooms[chatRoomName]) == 0:
                            chatRooms.pop(chatRoomName)
                        break

                    elif msg[:4] == "JOIN":
                        response = "ERROR. You have to exit first."
                        sendMessage(clientSocket, response)

                    else:
                        response = "HUH?\n"
                        sendMessage(clientSocket, response)

        elif msg[:4] == "LIST":
            response = [room for room in chatRooms]
            response = "ROOMS\t" + str(response)
            sendMessage(clientSocket, response)
            clientSocket.close()
            break

        else:
            response = "HUH?"
            sendMessage(clientSocket, response)
            clientSocket.close()
            break
        if not clientSocket._closed:
            msg = getMessage(clientSocket)


def joinRoom(msg, clientSocket, chatRooms, socketRooms):
    msg = msg.split()
    chatRoomName, UserName = msg[1], msg[2]
    if chatRoomName in chatRooms:
        if UserName in chatRooms[chatRoomName]:
            response = "Denied \t UserName not unique"
            sendMessage(clientSocket, response)
            clientSocket.close()
        else:
            chatRooms[chatRoomName].append(UserName)
            socketRooms[chatRoomName].append(clientSocket)
            response = "OK \t joined " + chatRoomName
            sendMessage(clientSocket, response)
    else:
        chatRooms[chatRoomName] = [UserName]
        socketRooms[chatRoomName] = [clientSocket]
        response = "OK \t" + chatRoomName + " created"
        sendMessage(clientSocket, response)
    return chatRoomName, UserName


def getIPAddress():
    s = socket(AF_INET, SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]


def getMessage(sock):
    data = sock.recv(1024)
    print(data.decode('ascii'))
    return data.decode('ascii')


def sendMessage(sock, msg):
    print(msg)
    sock.send(msg.encode('ascii'))


def sendError(s):
    errorMsg = "Unexpected response. Connection terminated."
    sendMessage(s, errorMsg)
    s.close()


chatServer()
