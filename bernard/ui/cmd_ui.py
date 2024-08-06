
class CmdUI: 
    def send(self, msg):
        print("Assistant: " + msg)
    async def receive(self):
        msg = input("User: ")
        return msg