import os
import socket
import threading
import constants as consts
from dotenv import load_dotenv


def sendMsg():
    while True:
        command = input()
        if command.lower() == "!users":
            client.send(consts.ClientRequest.list().encode("utf-8"))
        elif command.lower() == "!quit":
            print("Thank you for using our program! See you again.")
            client.close()
            return
        elif len(command.split(" ")) > 1:
            inputWords = command.split(" ")
            receiver = inputWords[0][1:]
            message = ' '.join(inputWords[1:])
            client.send(f'{consts.ClientRequest.send()}{receiver}\n{message}\n'.encode("utf-8"))
        else:
            print("Wrong command! Please try again.")

def recvMsg():
    while True:
        try:
            receivedMsg = ""
            while ("\n" not in receivedMsg):
                partOfMsg = client.recv(4096).decode("utf-8")
                receivedMsg += partOfMsg
            if consts.ServerResponses.okList() in receivedMsg:
                outputWords = receivedMsg.split('\n')
                availableUsers = outputWords[1]
                print(f'Available users: {availableUsers}')
            elif receivedMsg == consts.ServerResponses.unknown():
                print("Invalid or unavailable user")
            elif (consts.ServerResponses.delivery() in receivedMsg):
                outputWords = receivedMsg.split("\n")
                sender = outputWords[1]
                message = ' '.join(outputWords[2:])
                print(f'{sender}: {message}')
            elif receivedMsg == consts.ServerResponses.okSend():
                print("Message sent!")
            else:
                print(receivedMsg)
        except Exception as e:
            print(receivedMsg)
            client.close()
            return


if __name__ == "__main__":
    load_dotenv()
    host = os.getenv('IP_ADDRESS')
    port = int(os.getenv('PORT_NUMBER'))
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect((host, port))
        name = input("Please enter your name:\n")
        client.send(f'{consts.ClientRequest.hello()}{name}\n'.encode("utf-8"))
        receivedMsg = client.recv(4069).decode("utf-8")
        if consts.ServerResponses.hello() in receivedMsg:
            print("You logged in")
            senderThread = threading.Thread(target=sendMsg, daemon=True)
            receiverThread = threading.Thread(target=recvMsg, daemon=True)
            senderThread.start()
            receiverThread.start()
            senderThread.join()
        elif (receivedMsg == consts.ServerResponses.inUse()):
            print("User with such nickname already exists!")
            client.close()
        elif (receivedMsg == consts.ServerResponses.busy()):
            print("Servers is full!")
            client.close()
        else:
            print(receivedMsg)


