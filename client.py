import os
import constants as consts
import asyncio
from dotenv import load_dotenv


class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
    
    
    async def async_input(self, prompt: str = "") -> str:
        return await asyncio.get_event_loop().run_in_executor(None, input, prompt)


    async def sendMsg(self, writer):
        while True:
            command = await self.async_input()
            if command.lower() == "!users":
                writer.write(consts.ClientRequest.list().encode("utf-8"))
                await writer.drain()

            elif command.lower() == "!quit":
                print(consts.ClientResponses.thanks())
                writer.close()
                await writer.wait_closed()
                return
            
            elif len(command.split(" ")) > 1:
                inputWords = command.split(" ")
                receiver = inputWords[0][1:]
                message = ' '.join(inputWords[1:])
                writer.write(f'{consts.ClientRequest.send()}{receiver}\n{message}\n'.encode("utf-8"))
                await writer.drain()

            else:
                print(consts.Error.wrongCommand())
    

    async def getMsgFromSocket(self, reader):
        receivedMsg = ""
        while not receivedMsg.endswith("\n"):
            chunk = await reader.read(4096)
            if not chunk:
                break
            receivedMsg += chunk.decode("utf-8")
            print("msg received:", receivedMsg)

        return receivedMsg
    

    async def printAvailableUsers(self, receivedMsg):
        availableUsers = receivedMsg.split("\n")[1]
        await asyncio.sleep(1/1000.0)
        print(f'Available users: {availableUsers}')


    async def printReceivedMsg(self, receivedMsg):
        outputWords = receivedMsg.split("\n")
        sender = outputWords[1]
        message = ' '.join(outputWords[2:])
        await asyncio.sleep(1/1000.0)
        print(f'{sender}: {message}')


    async def recvMsg(self, reader):
        while True:
            try:
                receivedMsg = await self.getMsgFromSocket(reader)
                if consts.ServerResponses.okList() in receivedMsg:
                    await self.printAvailableUsers(receivedMsg)
                elif receivedMsg == consts.ServerResponses.unknown():
                    print(consts.Error.invalidOrUnvalidUser())
                elif consts.ServerResponses.delivery() in receivedMsg:
                    await self.printReceivedMsg(receivedMsg)
                elif receivedMsg == consts.ServerResponses.okSend():
                    print(consts.ClientResponses.msgSent())
                else:
                    print(receivedMsg)
            except Exception as e:
                print(consts.Error.errorStartingTasks(str(e)))
                return
                
    async def run(self):
        try:
            reader, writer = await asyncio.open_connection(self.host, self.port)
                
            name = await self.async_input("Please enter your name:\n") 
            writer.write(f'{consts.ClientRequest.hello()}{name}\n'.encode("utf-8"))
            await writer.drain()
            receivedMsg = await self.getMsgFromSocket(reader)
            if consts.ServerResponses.hello() in receivedMsg:
                print(consts.ClientResponses.loggedIn())
                senderTask = asyncio.create_task(self.sendMsg(writer))
                receiverTask = asyncio.create_task(self.recvMsg(reader))
                await asyncio.gather(senderTask, receiverTask)
            elif receivedMsg == consts.ServerResponses.inUse():
                print(consts.Error.usernameExists())
            elif receivedMsg == consts.ServerResponses.busy():
                print(consts.Error.serverIsFull())
            else:
                print(receivedMsg)

            writer.close()
            await writer.wait_closed()
        except Exception as e:
            print(consts.Error.errorStartingTasks(str(e)))



if __name__ == "__main__":
    load_dotenv()
    host = os.getenv('IP_ADDRESS')
    port = int(os.getenv('PORT_NUMBER'))
    client = Client(host, port)
    asyncio.run(client.run())


