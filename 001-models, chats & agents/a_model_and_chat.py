from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from dotenv import load_dotenv

load_dotenv()

model = ChatOpenAI(model = "gpt-4o")

message = "What is the best place on Earth?"

result = model.invoke(message)

from message_visualizer import print_messages
print_messages(result)

input("Press Enter to continue...")

messages = [
    SystemMessage("You are a helpfull assistant, to help me answer questions"),
    HumanMessage("which is the best place on earth?"),
    AIMessage ("""The concept of the "best" place on Earth is subjective and depends 
               on individual preferences, interests, and experiences. 
               Some people might consider natural wonders like the Grand Canyon, 
               the Great Barrier Reef, or Mount Everest as the best places due to their 
               breathtaking beauty. Others might prefer vibrant cities like Paris, Tokyo, 
               or New York for their culture, cuisine, and entertainment. For those seeking tranquility, 
               destinations like the Maldives or the Swiss Alps might be ideal. Ultimately,
               the best place is where you find joy, fulfillment, and a sense of belonging."""),
       HumanMessage("I am looking for the place with the best food"),           
]
result = model.invoke(messages)
print_messages(result)
input("Press Enter to continue...")

messages = [
    SystemMessage("You are a helpfull assistant, to help me answer questions"),
]

while True:
    q = input("Ask a question: ")
    if q == "exit":
        break
    if q == "print":   
        print_messages(messages)
        continue
    if q== "reset":
        messages = [
            SystemMessage("You are a helpfull assistant, to help me answer questions"),
        ]
        continue

    messages.append(HumanMessage(q))
    a = model.invoke(messages)
    print(a.content)
    messages.append(AIMessage(a.content))
