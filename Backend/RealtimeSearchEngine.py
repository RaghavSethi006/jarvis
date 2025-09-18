from googlesearch import search
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
client = Groq(api_key=GroqAPIKey)

#define the system prompt that guides the model on how to respond.
System_prompt =f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {AssistantName} which has real-time up-to-date information from the internet.
*** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.***
*** Just answer the question from the provided data in a professional way. ***"""

#try to load the chat history from a file.
try:
    with open(r'Data\ChatLog.json', 'r') as file:
        messages = load(file)
except :
    with open(r'Data\ChatLog.json', 'w') as file:
        dump([], file)  

#function to realtime googleearch and forma the results 
def GoogleSearch(query):
    results = list(search(query, advanced=True ,num_results=5))
    Answers = f"the search resutls for '{query}' are:\n [start]\n"

    for i in results:
        Answers+= f"tittle:{i.title}\n description : {i.description}\n\n" #type: ignore
    Answers += "[end]"
    return Answers

#functon to clean the search results
def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer

#predefined chat history to provide context to the model.
SystemChatBot = [
    {"role" : "system" , "content" : System_prompt},
    {"role":"user","content":"hi"},
    {"role":"assistant","content":"hello, how can i help you today?"}
]

#function to get realtime date and time information.
def Infromation():
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

#function to handle realtime search queries.
def RealtimeSearchEngine(query: str):
    global SystemChatBot, messages

    #load the chat history from the file.
    with open(r'Data\ChatLog.json', 'r') as file:
        messages = load(file)
    messages.append({"role": "user", "content": f"{query}"})

    #add google search results to the system chatbot messages.
    SystemChatBot.append({"role":"system","content":GoogleSearch(query)})

    #generate a response using the Groq model.
    completion = client.chat.completions.create(
        model="llama3-70b-8192",
        messages= SystemChatBot + [{"role":"system","content":Infromation()}] + messages,
        temperature=0.7,
        max_tokens=2048,
        top_p=1,
        stop=None,
        stream=True,
    )

    Answer = ""

    #process  the streams response chunks.
    for chunk in completion:
        if chunk.choices[0].delta.content:
            Answer += chunk.choices[0].delta.content
        
    Answer=Answer.replace("</s>", "")
    #appedn the chatbot's response to the messages list.
    messages.append({"role": "assistant", "content": Answer})
    #save the updated chat history to the file.
    with open(r'Data\ChatLog.json', 'w') as file:
        dump(messages, file, indent=4)  
    #return the modified answer.
    SystemChatBot.pop()
    return AnswerModifier(Answer)

if __name__ == "__main__":  
    while True:
        user_input = input("enter your query: ")
        print(RealtimeSearchEngine(user_input))