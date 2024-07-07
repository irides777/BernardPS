import streamlit as st
from openai import OpenAI
import time
import os

prompt = '''
我们将日常工作生活中的一段活动或一组连续的活动定义为事件。比如说一场面试、一次约会、一次阅读都是事件。
事件可以分为如下三种类型：
单点事件：这种事件有固定的开始时间，并且不需要提前做准备，比如参加讲座、收看电视节目等。
射线事件：这种事件有固定的截止时间，需要提前一段时间完成或做准备，比如论文投稿，期末大作业，准备考试等。
直线事件：这种事件没有固定的开始或截止时间，一般是在一定的周期内进行循环，比如每天阅读，每天运动等。
当你收到用户发来的一段消息时，请你首先判断该消息是否属于对一件未来事件的描述。如果属于对未来事件的描述，则对该事件进行分类。如果不属于，则分类为非事件。如果该事件发生在过去，也分类为非事件。
注意，你的分类应以json格式返回，格式为：{"class":"类别"}。
例1：
用户：下周二下午要面试
你：{"class":"射线事件"}
例2：
用户：明天晚上7点看球赛
你：{"class":"单点事件"}
例3：
用户：每天晚上要运动
你：{"class":"直线事件"}
例4：
用户：今天考试太难了，好讨厌
你：{"class":"非事件"}

现在请你判断，用户：
'''

if 'messages' not in st.session_state:
    st.session_state.messages = []

st.title('Chat with AI')
st.write('Type a message and press Enter to chat with AI.')

def process_input(user_input):
    client = OpenAI(
        api_key=os.getenv("DASHSCOPE_API_KEY"), # 如果您没有配置环境变量，请在此处用您的API Key进行替换
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",  # 填写DashScope服务的base_url
    )
    completion = client.chat.completions.create(
        model="qwen2-72b-instruct",
        # messages=[{'role': 'system', 'content': 'You are a helpful assistant.'},
        #           {'role': 'user', 'content': user_input}]
        messages=[{'role': 'user', 'content': prompt+user_input}]
        # messages=st.session_state.messages
    )
    return completion.choices[0].message.content

for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

if user_input := st.chat_input('user', key='user_input'):
    st.session_state.messages.append({'role':'user','content':user_input})
    with st.chat_message('user'):
        st.markdown(user_input)
    # Process user input
    response = process_input(user_input)
    st.session_state.messages.append({'role':'assistant','content':response})
    with st.chat_message('assistant'):
        st.markdown(response)