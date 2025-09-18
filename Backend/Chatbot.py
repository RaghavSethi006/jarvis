import re
from groq import Groq
from json import dump, load
import datetime
from dotenv import dotenv_values


#load environment variables from the .env file.
env_vars = dotenv_values(".env")
# Retrieve API key username and assistant name.
GroqAPIKey = env_vars.get("GroqAPIKey") 
Username = env_vars.get("Username")
AssistantName = env_vars.get("AssistantName")

#initialize the groq client with the API key.
groq = Groq(api_key=GroqAPIKey)

#intitialize an empty list to store chat messages.
messages = []

#define the system prompt that guides the model on how to respond.
System_prompt = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {AssistantName} which also has real-time up-to-date information from the internet.
*** Do not tell time until I ask, do not talk too much, just answer the question.***
*** Reply in only English, even if the question is in Hindi, reply in English.***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***
"""

#a list of systum instructions that guide the model on how to categorize queries.
systemChatBot = [
    {"role": "system", "content": System_prompt}
]

#attempt to load the chat history from a file.
try:
    with open(r'Data\ChatLog.json', 'r') as file:
        messages = load(file)
except FileNotFoundError:
    with open(r'Data\ChatLog.json', 'w') as file:
        dump([], file)

#function to get realtime date and time information.
def RealtimeInfromation():
    current_date_time = datetime.datetime.now()
    day= current_date_time.strftime("%A")
    date = current_date_time.strftime("%d")
    month = current_date_time.strftime("%B")
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%H")
    minute = current_date_time.strftime("%M")       
    second = current_date_time.strftime("%S")

    #Format the information into a string.
    data = f"please use this realtime information if needed day:{day}, date:{date}, month: {month}, year: {year}, hour: {hour}, minutes:{minute}, seconds:{second}"
    return data 

#function to modify the chatbots response for better formating 
def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer

#main chatbot function that handles user queries.
def ChatBot(query: str):
    
    try:
        #load the chat history from the file.
        with open(r'Data\ChatLog.json', 'r') as file:
            messages = load(file)
        
        #append the user query to the messages list.
        messages.append({"role": "user", "content": f"{query}"})

        #make a request to the Groq model with the chat history and system instructions.
        compeletion = groq.chat.completions.create(
            model="llama3-70b-8192",
            messages= systemChatBot + [{"role":"system","content":RealtimeInfromation()}] + messages,
            temperature=0.7,
            max_tokens=1024,
            top_p=1,
            stop=None,
            stream=True,
        )

        Answer=""

        #process  the streams response chunks.
        for chunk in compeletion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content
            
        Answer=Answer.replace("</s>", "")

        #appedn the chatbot's response to the messages list.
        messages.append({"role": "assistant", "content": Answer})

        #save the updated chat history to the file.
        with open(r'Data\ChatLog.json', 'w') as file:
            dump(messages, file, indent=4)  

        #return the modified answer.
        return AnswerModifier(Answer)
    
    except Exception as e:
        #handle any exceptions that occur during the process.
        print(f"An error occurred: {e}")
        with open(r'Data\ChatLog.json', 'w') as file:
            dump([], file, indent=4)
        return ChatBot(query)
    
#entry point for the module, allowing it to be run as a script.
if __name__ == "__main__":  
    while True:
        user_input = input("enter your query: ")
        print(ChatBot(user_input))