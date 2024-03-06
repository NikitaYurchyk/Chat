import os
import socket
import threading
from dotenv import load_dotenv
import constants as consts


class Server:
    def __init__(self, host, port):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen()
        self.users = {}  

    def sendResponse(self, client, message):
        client.send(message.encode("utf-8"))

    def receiveMsg(self, client):
        while True:
            try:
                receivedMsg = ""
                while "\n" not in receivedMsg:
                    receivedMsg += client.recv(4096).decode("utf-8")
                self.processMessage(client, receivedMsg)
            except Exception as e:
                print(e)
                self.disconnectClient(client)
                return

    def processMessage(self, client, msg):
        if consts.ClientRequest.hello() in msg:
            self.handleHello(client, msg)
        elif msg == consts.ClientRequest.list():
            self.handleList(client)
        elif consts.ClientRequest.send() in msg:
            self.handleSend(client, msg)
        else:
            sentMsg = consts.ServerResponses.badRequestHeader()
            self.sendResponse(client, sentMsg)

    def handleHello(self, client, msg):
        inputWords = msg.split("\n")
        # print("here", msg, inputWords)
        if (len(inputWords) > 3 and inputWords[2] == '') or len(inputWords) == 1:
            sentMsg = consts.ServerResponses.badRequestBody()
            self.sendResponse(client, sentMsg)
            return
        
        elif len(self.users) == 10:
            sentMsg = consts.ServerResponses.busy()
            self.sendResponse(client, sentMsg)
            return
        
        else:
            name = inputWords[1].replace("\n", "")
            if name in self.users:
                sentMsg = consts.ServerResponses.inUse()
                self.sendResponse(client, sentMsg)
                return
            
            else:
                self.users[name] = client
                sentMsg = f'{consts.ServerResponses.hello()}{name}\n'
                self.sendResponse(client, sentMsg)

    def handleList(self, client):
            availableUsers = ", ".join(self.users.keys())
            sentMsg =  f'{consts.ServerResponses.okList()}{availableUsers}\n'
            self.sendResponse(client, sentMsg)


    def handleSend(self, client, msg):
            inputWords = msg.split("\n")
            if (len(inputWords) < 3):
                sentMsg = consts.ServerResponses.badRequestBody()
                self.sendResponse(client, sentMsg)
            else:
                receiverName = inputWords[1]
                if receiverName not in self.users:
                    sentMsg = consts.ServerResponses.noUserInDb()
                    self.sendResponse(client, sentMsg)  
                
                else:
                    message = " ".join(inputWords[2:])
                    sentMsgToClient = consts.ServerResponses.okSend()
                    sentMsgToReceiver = f'{consts.ServerResponses.delivery()}{inputWords[1]}\n{message}\n'
                    self.sendResponse(client, sentMsgToClient)
                    self.sendResponse(self.users.get(receiverName), sentMsgToReceiver)  

    def disconnectClient(self, client):
        clientName = [key for key, val in self.users.items() if val == client][0]
        self.users.pop(clientName)
        print("closing server")
        client.close()

    def run(self):
        print("server is listening...")
        while True:
            client, address = self.server.accept()
            print(f'Connected with {str(address)}')
            thread = threading.Thread(target=self.receiveMsg, args=(client,))
            thread.daemon = True
            thread.start()
            if not thread.is_alive:
                thread.join()
                break


if __name__ == "__main__":
    load_dotenv()
    host = os.getenv('IP_ADDRESS')
    port = os.getenv('PORT_NUMBER')
    server = Server(host, int(port))
    server.run()

