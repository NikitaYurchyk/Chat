import os
import asyncio
import db
from dotenv import load_dotenv
import constants as consts


class Server:
    def __init__(self, host, port, db):
        self.host = host
        self.port = port
        self.db = db
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
            print("list sent")

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
            await self.sendResponse(writer, sentMsgToClient)
            await self.sendResponse(self.users[receiverName], sentMsgToReceiver)

    async def disconnectClient(self, writer):
        clientName = next((key for key, val in self.users.items() if val == writer), None)
        if clientName:
            self.users.pop(clientName)
            print(f"Disconnected: {clientName}")
        writer.close()
        await writer.wait_closed()

    async def run(self):
        print("server is listening...")
        server = await asyncio.start_server(self.receiveMsg, self.host, self.port)

        async with server:
            await server.serve_forever()

async def main():
    load_dotenv()
    host = os.getenv('IP_ADDRESS')
    port = os.getenv('PORT_NUMBER')
    dataBase = await db.AsyncDatabase()
    server = Server(host, int(port))
    asyncio.run(server.run())

asyncio.run(main())

