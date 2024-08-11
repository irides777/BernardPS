
import sys
import asyncio
class CmdUI: 
    def send(self, msg):
        print("Assistant: " + msg)

    async def ainput(self, string: str) -> str:
        await asyncio.to_thread(sys.stdout.write, f'{string} ')
        sys.stdout.flush()
        return (await asyncio.to_thread(sys.stdin.readline)).rstrip('\n')

    async def receive(self):
        # msg = ainput("User: ")
        msg = await self.ainput("User: ")
        return msg