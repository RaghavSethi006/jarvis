
from AppOpener import close , open as appopen
from webbrowser import open as webopen 
from pywhatkit.misc import search ,playonyt
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print 
from groq import Groq
import webbrowser
import subprocess
import requests
import keyboard
import asyncio
import os 

#load environment variables
env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Define CSS classes for parsing specific elements in HTML content. |
classes = ["zCubwf", "hgKElc", "LTKOO sY7ric", "ZOLcW", "gsrt vk_bk FzvWSb YwPhnf", "pclgee", "tw-Data-text tw-text-small tw-ta",
"IZérdc", "O5uR6d LTKOO", "vlzY6d", "webanswers-webanswers_table__webanswers-table", "dDoNo ikb4Bb gsrt", "sXLaOe",
"LwkfKe", "VQF4g", "qv3Wpe", "kno-rdesc", "SPZz6b"] 

#define user agent for web requests
useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36' 

# Initialize Groq client
client = Groq(api_key=GroqAPIKey)

#predefine professional responses for user interactions
professional_responses = [
    "Your satisfaction is my top priority; feel free to reach out if there's anything else I can help you with.",
    "I'm at your service for any additional questions or support you may need—don't hesitate to ask.",
]

#lit to store chatbot messages
messages = []

#system message to set the tone of the chatbot
SystemChatBot = [{"role":"system", "content": f"Hello, i am {os.environ['username']},You're a content writer. you have to write content like letter"}]

#function to perform google search
def GoogleSearch(topic):
    search(topic)
    return True

#function to generate content using AI and save it to a file
def Content(topic):

    #nested function to open a file in Notepad.
    def OpenNotepad(File):
        default_text_editor = "notepad.exe"
        subprocess.Popen([default_text_editor, File])

    def ContentWrterAI(promt):
        messages.append({"role": "user", "content": f"{promt}"})

        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages= SystemChatBot + messages, #type: ignore
            max_tokens=2048,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None
        )

        Answer = ""

        #process streamed responses chunks 
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer+= chunk.choices[0].delta.content

        Answer = Answer.replace("</s>", " ")
        messages.append({"role": "assistant", "content": Answer})
        return Answer
    
    Topic: str = topic.replace("Content ", "")
    ContentByAI = ContentWrterAI(Topic)

    #save the generated content to a file 
    with open(rf"Data\{Topic.lower().replace(' ','_')}.txt",'w', encoding='utf-8') as f:
        f.write(ContentByAI)
        f.close()

        OpenNotepad(rf"Data\{Topic.lower().replace(' ','')}.txt")
        return True

#function to search on yt 
def YouTubeSearch(topic):
    Url4Search = f"https://www.youtube.com/results?search_query={topic}"
    webbrowser.open(Url4Search)
    return True

#function to play a video on YouTube
def PlayYoutube(topic):
    playonyt(topic)
    return True

#function to open app 
def OpenApp(app, sess=requests.session()):

    try:
        appopen(app,match_closest=True , output=True, throw_error=True)
        return True
    
    except:
        #nested function to extract links from html content
        def extract_links(html):
            if html is None:
                return []
            soup = BeautifulSoup(html, 'html.parser')
            links = soup.find_all('a', {'jsname':'UWckNb'})
            return [link.get('href') for link in links] # type: ignore
        
        #nested function to perform a google search and retirve HTML
        def google_search(query):
            url=   f"https://www.google.com/search?q={query}"
            headers = {'User-Agent': useragent}
            response = sess.get(url, headers=headers)

            if response.status_code == 200:
                return response.text
            else:
                print("failed to retrive search results.")

            return None
        
        html = google_search(app)

        if html:
            link = extract_links(html)[0]
            webopen(link) # type: ignore

        return True

#function to close an app
def CloseApp(app):

    if "chrome" in app:
        pass
    else:
        try:
            close(app, match_closest=True, output=True, throw_error=True)
            return True
        except:
            return False
     
#function to excecute system level commands 
def System(command):

    #nested function to mute the system volume
    def mute():
        keyboard.press_and_release('volume mute')

    #nested function to unmute the system volume
    def unmute():
        keyboard.press_and_release('volume unmute')
    
    #nested function to increase the system volume
    def increase_volume():
        keyboard.press_and_release('volume up')
    
    #nested function to decrease the system volume
    def decrease_volume():  
        keyboard.press_and_release('volume down')

    #Execute system commands based on the input command
    if command == "mute":
        mute()
        return True
    elif command == "unmute":
        unmute()
        return True
    elif command == "increase volume":
        increase_volume()
        return True
    elif command == "decrease volume":
        decrease_volume()
        return True
    else:
        print("Invalid system command.")
        return False
    
#asynchronous function to handle user queries
async def TranslateAndExecute(commands : list[str]):

    funcs= [] 

    for command in commands:

        if command.startswith("open "):
            
            if "open it" in command:
                pass

            if "open file" in command:
                pass

            else:
                fun = asyncio.to_thread(OpenApp, command.removeprefix("open "))
                funcs.append(fun)
            
        elif command.startswith("general"):
            pass

        elif command.startswith("realtime "):
            pass 

        elif command.startswith("close "):
            fun = asyncio.to_thread(CloseApp, command.removeprefix("close "))
            funcs.append(fun)

        elif command.startswith("play "):
            fun = asyncio.to_thread(PlayYoutube, command.removeprefix("play "))
            funcs.append(fun)

        elif command.startswith("content "):
            fun =   asyncio.to_thread(Content, command.removeprefix("content "))
            funcs.append(fun)

        elif command.startswith("google search "):
            fun = asyncio.to_thread(GoogleSearch, command.removeprefix("google search "))
            funcs.append(fun)

        elif command.startswith("youtube search "):
            fun = asyncio.to_thread(YouTubeSearch, command.removeprefix("youtube search "))
            funcs.append(fun)

        elif command.startswith("system "):
            fun = asyncio.to_thread(System, command.removeprefix("system "))
            funcs.append(fun)
        
        else:
            print(f'no function found for command: {command}')

    resuls= await asyncio.gather(*funcs)

    for result in resuls:
        if isinstance(result, str):
            yield result
        else:
            yield result 
    
#asynchronous function to automate command execution 
async def Automation(commands: list[str]):

    async for result in TranslateAndExecute(commands):
        pass
    return True
