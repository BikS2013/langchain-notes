from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnableLambda
from dotenv import load_dotenv

load_dotenv()


import os
model = ChatGoogleGenerativeAI(model = "gemini-1.5-pro")
model = ChatOpenAI(
    model="deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_BASE_URL"), 
    temperature=0,
)

template = "calculate the square of {x}"

prompt_template = ChatPromptTemplate.from_template(template)

prompt = prompt_template.invoke({ "x": 12 })
result = model.invoke(prompt)
from message_visualizer import print_messages
print_messages(result)
input ("Press Enter to continue...")

messages_template = [
    ("system", """You are a sysstem capable of calculating arithmetic expressions. 
            You must answer any question returning the result and a detailed explanation of the approach you followed to find it."""),
    ("human", "calculate the square of {x}"),
]

prompt_template = ChatPromptTemplate.from_messages(messages_template)
messages = prompt_template.invoke({"x": 12})

result = model.invoke(messages)
print_messages(result)
input ("Press Enter to continue...")

chain = prompt_template | model 
result = chain.invoke({"x": 12}) 
print_messages(result)
input ("Press Enter to continue...")

print_result = RunnableLambda(lambda x: print(x))  

print_content = RunnableLambda(lambda x: ( 
    print(x.content), 
    x
    )
)

chain = prompt_template | model | print_content

result = chain.invoke({ "x": 1350 })
print_messages(result)
