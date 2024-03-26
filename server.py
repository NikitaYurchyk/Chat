import os
import asyncio
import db
from dotenv import load_dotenv
import constants as consts


class Server:
    def __init__(self, host, port, database):
        self.host = host
        self.port = port
        self.database = database
        self.users = {}
        self.lock = asyncio.Lock()

    async def sendResponse(self, writer, message):
        writer.write(message.encode("utf-8"))
        await writer.drain()

    async def receiveMsg(self, reader, writer):
        while True:
            try:
                receivedMsg = ""
                while not receivedMsg.endswith("\n"):
                    chunk = await reader.read(4096)
                    if not chunk:
                        break
                    receivedMsg += chunk.decode("utf-8")
                print(receivedMsg)
                if receivedMsg:
                    await self.processMessage(writer, receivedMsg)
                else:
                    await self.disconnectClient(writer)
                    break
            except Exception as e:
                print(e)
                await self.disconnectClient(writer)
                return

    async def processMessage(self, writer, msg):
        if consts.ClientRequest.hello() in msg:
            await self.handleHello(writer, msg)
        elif msg == consts.ClientRequest.list():
            await self.handleList(writer)
        elif consts.ClientRequest.send() in msg:
            await self.handleSend(writer, msg)
        elif consts.ClientRequest.askForHistory():
            await self.sendMessages(writer)
        else:
            sentMsg = consts.ServerResponses.badRequestHeader()
            await self.sendResponse(writer, sentMsg)

    async def handleHello(self, writer, msg):
        inputWords = msg.split("\n")
        print(inputWords)
        if (len(inputWords) > 3 and inputWords[2] == '') or len(inputWords) == 1:
            sentMsg = consts.ServerResponses.badRequestBody()
            await self.sendResponse(writer, sentMsg)
            return

        elif len(self.users) == 10:
            sentMsg = consts.ServerResponses.busy()
            await self.sendResponse(writer, sentMsg)
            return

        else:
            name = inputWords[1].replace("\n", "")
            if name in self.users:
                sentMsg = consts.ServerResponses.inUse()
                await self.sendResponse(writer, sentMsg)
                return

            else:
                async with self.lock:
                    self.users[name] = writer
                sentMsg = f'{consts.ServerResponses.hello()}{name}\n'
                await self.sendResponse(writer, sentMsg)

    async def handleList(self, writer):
        availableUsers = ", ".join(self.users.keys())
        sentMsg = f'{consts.ServerResponses.okList()}{availableUsers}\n'
        await self.sendResponse(writer, sentMsg)

    async def handleSend(self, writer, msg):
        inputWords = msg.split("\n")
        if (len(inputWords) < 3):
            sentMsg = consts.ServerResponses.badRequestBody()
            await self.sendResponse(writer, sentMsg)
            return

        receiverName = inputWords[1]
        if receiverName not in self.users:
            sentMsg = consts.ServerResponses.noUserInDb()
            await self.sendResponse(writer, sentMsg)
            return

        message = "\n".join(inputWords[2:])
        sentMsgToClient = consts.ServerResponses.okSend()
        sentMsgToReceiver = f'{consts.ServerResponses.delivery()}{receiverName}\n{message}\n'
        senderName = next((key for key, val in self.users.items() if val == writer), None)
        await self.database.sendMessage(receiverName, senderName, message)
        await self.sendResponse(writer, sentMsgToClient)
        await self.sendResponse(self.users[receiverName], sentMsgToReceiver)
        print(sentMsgToClient)
        print(sentMsgToReceiver)
    async def prepareMsg(self, lst) -> str:
        msg = ""
        for word in lst:
            # problem with encrypted messages
            msg += word[0] + " " + word[1] + " " + word[3][:-1] + "\n"
        return msg

    async def sendMessages(self, writer):
        senderName = next((key for key, val in self.users.items() if val == writer), None)
        lst = await self.database.getMessages(senderName)
        msg = f'{consts.ServerResponses.history()}' + await self.prepareMsg(lst)

        await self.sendResponse(writer, msg)
        print(lst)


    async def disconnectClient(self, writer):
        clientName = next((key for key, val in self.users.items() if val == writer), None)
        if clientName:
            self.users.pop(clientName)
            print(f"Disconnected: {clientName}")
        writer.close()
        await writer.wait_closed()

    async def run(self):
        print("server is listening...")
        await self.database.initialize_db()
        server = await asyncio.start_server(self.receiveMsg, self.host, self.port)

        async with server:
            await server.serve_forever()


async def main():
    load_dotenv()
    host = os.getenv('IP_ADDRESS')
    port = os.getenv('PORT_NUMBER')
    dataBase = db.AsyncDatabase()
    server = Server(host, int(port), dataBase)
    await server.run()


asyncio.run(main())

