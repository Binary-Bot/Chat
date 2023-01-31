from socket import *
import threading
import sys


def getIPAddress():
    s = socket(AF_INET, SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]


def getMessage(sock):
    data = sock.recv(1024)
    return data.decode('ascii')


def sendMessage(sock, msg):
    sock.send(msg.encode('ascii'))


def chatClient():
    i = True
    s = socket()
    IP = input("Enter the IP address of the server: ")
    s.connect((IP, 2028))
    command = input("JOIN or LIST: ")
    if command[:4] == 'JOIN':
        while s.fileno() != -1:
            threading.Thread(target=sending, args=(s, command)).start()
            threading.Thread(target=receiveMsgs, args=(s, i)).start()
            command = input("->")
            if command == "LIST":
                sendMessage(s, command)
                print(getMessage(s))
                s.close()

        s.close()
    elif command[:4] == "LIST":
        sendMessage(s, command)
        print(getMessage(s))
        s.close()

    else:
        sendMessage(s, command)
        print(getMessage(s))
    return 0


def sending(s, command):
    sendMessage(s, command)


def receiveMsgs(s, i):
    while s.fileno() != -1:
        try:
            response = getMessage(s)
            print(response)
        except:
            break


chatClient()
