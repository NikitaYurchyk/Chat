import os

import constants
import constants as consts
import asyncio
from dotenv import load_dotenv


class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    async def recvMsg(self, reader):
        while True:
            try:
                receivedMsg = await self.getMsgFromSocket(reader)
                if consts.ServerResponses.okList() in receivedMsg:
                    await self.printAvailableUsers(receivedMsg)
                if consts.ServerResponses.history() in receivedMsg:
                    print(receivedMsg)

                elif consts.ServerResponses.unknown() in receivedMsg:
                    print(consts.Error.invalidOrUnvalidUser(), end="")
                elif consts.ServerResponses.delivery() in receivedMsg:
                    await self.printReceivedMsg(receivedMsg)
                elif consts.ServerResponses.okSend() in receivedMsg:
                    print(consts.ClientResponses.msgSent())
                else:
                    print(receivedMsg, end="")
            except Exception as e:
                print(consts.Error.errorStartingTasks(str(e)), end="")
                return

    async def sendMsg(self, writer):
        while True:
            command = await self.asyncInput()
            if command.lower() == "!users":
                await self.sendMsgToSocket(writer, consts.ClientRequest.list())
            elif command.lower() == "!quit":
                await self.quit(writer)
                return
            elif command.lower() == "!commands":
                print(constants.ClientRequest.askForCommand())
            elif command.lower() == "!history":
                await self.sendMsgToSocket(writer, consts.ClientRequest.askForHistory())
            elif "@" in command and len(command.split(" ")) > 1:
                parsedCommand = await self.parseCmdMsg(command)
                await self.sendMsgToSocket(writer, parsedCommand)
            else:
                print(consts.Error.wrongCommand())

    async def asyncInput(self, prompt: str = "") -> str:
        return await asyncio.get_event_loop().run_in_executor(None, input, prompt)

    async def parseCmdMsg(self, command: str) -> str:
        inputWords = command.split(" ")
        receiver = inputWords[0][1:]
        message = ' '.join(inputWords[1:])
        return f'{consts.ClientRequest.send()}{receiver}\n{message}\n'

    async def sendMsgToSocket(self, writer, command: str) -> None:
        writer.write(command.encode("utf-8"))
        await writer.drain()

    async def quit(self, writer):
        print(consts.ClientResponses.thanks())
        writer.close()
        await writer.wait_closed()

    async def getMsgFromSocket(self, reader):
        receivedMsg = ""
        while not receivedMsg.endswith("\n"):
            chunk = await reader.read(4096)
            if not chunk:
                break
            receivedMsg += chunk.decode("utf-8")
        return receivedMsg

    async def printAvailableUsers(self, receivedMsg):
        availableUsers = receivedMsg.split("\n")[1]
        await asyncio.sleep(1 / 1000.0)
        print(f'Available users: {availableUsers}')

    async def printReceivedMsg(self, receivedMsg):
        outputWords = receivedMsg.split("\n")
        sender = outputWords[1]
        message = ' '.join(outputWords[2:])
        await asyncio.sleep(1 / 1000.0)
        print("received a new msg from " + sender + ": " + message)

    async def run(self):
        try:
            reader, writer = await asyncio.open_connection(self.host, self.port)
            name = await self.asyncInput("Please enter your name:\n")
            writer.write(f'{consts.ClientRequest.hello()}{name}\n'.encode("utf-8"))
            await writer.drain()
            receivedMsg = await self.getMsgFromSocket(reader)
            if consts.ServerResponses.hello() in receivedMsg:
                print("\n\n@@@@ --- @@@@",end="\n\n")
                print(consts.ClientResponses.loggedIn(), end="\n\n@@@@ --- @@@@\n\n")
                print(constants.ClientRequest.askForCommand(), end="")
                senderTask = asyncio.create_task(self.sendMsg(writer))
                receiverTask = asyncio.create_task(self.recvMsg(reader))
                await asyncio.gather(senderTask, receiverTask)
            elif receivedMsg == consts.ServerResponses.inUse():
                print(consts.Error.usernameExists(), end="")
            elif receivedMsg == consts.ServerResponses.busy():
                print(consts.Error.serverIsFull(), end="")
            else:
                print(receivedMsg, end="")
            writer.close()
            await writer.wait_closed()
        except Exception as e:
            print(consts.Error.errorStartingTasks(str(e)), end="")


if __name__ == "__main__":
    load_dotenv()
    host = os.getenv('IP_ADDRESS')
    port = int(os.getenv('PORT_NUMBER'))
    client = Client(host, port)
    asyncio.run(client.run())
