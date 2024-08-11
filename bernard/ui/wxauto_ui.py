
import sys
import asyncio

from wxauto import WeChat

class WxautoUI: 

    def __init__(self, wx_window: WeChat, user_name):
        self.wx_window = wx_window
        self.user_name = user_name

        self.wx_window.AddListenChat(who=user_name)

    def send(self, msg):
        self.wx_window.SendMsg(msg=msg, who=self.user_name)

    async def receive(self):
        # msg = ainput("User: ")
        while True:
            await asyncio.sleep(1)
            msgs = self.wx_window.GetListenMessage()
            for chat in msgs:
                if chat.who == self.user_name:
                    one_msgs = msgs.get(chat)   # 获取消息内容
                    for msg in one_msgs:
                        if msg.type == 'friend':
                            print(chat.who, msg.content)
                            # break
                            return msg.content
                
            # print('---------------')