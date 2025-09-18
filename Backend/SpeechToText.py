from asyncio import IncompleteReadError
from pydoc import text
from xml.sax.xmlreader import IncrementalParser
from selenium import webdriver
from selenium.webdriver.chrome.service import Service   
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options       
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import dotenv_values
import os 
import mtranslate as mt

# Load environment variables from the .env file.
env_vars = dotenv_values(".env")

#get input language and output language from environment variables.
InputLanguage = str(env_vars.get("InputLanguage"))

#define the html code for the speech recognition interface 
html_code = '''<!DOCTYPE html>
<html lang="en">
<head>
    <title>Speech Recognition</title>
</head>
<body>
    <button id="start" onclick="startRecognition()">Start Recognition</button>
    <button id="end" onclick="stopRecognition()">Stop Recognition</button>
    <p id="output"></p>
    <script>
        const output = document.getElementById('output');
        let recognition;

        function startRecognition() {
            recognition = new webkitSpeechRecognition() || new SpeechRecognition();
            recognition.lang = '';
            recognition.continuous = true;

            recognition.onresult = function(event) {
                const transcript = event.results[event.results.length - 1][0].transcript;
                output.textContent += transcript;
            };

            recognition.onend = function() {
                recognition.start();
            };
            recognition.start();
        }

        function stopRecognition() {
            recognition.stop();
            output.innerHTML = "";
        }
    </script>
</body>
</html>'''

#replace the input language in the html code.
html_code =str(html_code).replace("recognition.lang = '';",f"recognition.lang= '{InputLanguage}'; ") 

#wrtie the modified html code to a file.
with open("Data\\Voice.html", "w", encoding="utf-8") as file:
    file.write(html_code)

#get the current working directory.
current_directory = os.getcwd()

#generate the path to the html file.
Link = f"{current_directory}\\Data\\Voice.html"

#set the options for the chrom webdriver.
chrome_options = Options()
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"   
chrome_options.add_argument(f"user-agent={user_agent}")
chrome_options.add_argument("--use-fake-ui-for-media-stream")
chrome_options.add_argument("--use-fake-device-for-media-stream")
chrome_options.add_argument("--headless=new")

#initialize the chromedriver service.
service = Service(ChromeDriverManager().install())
#initialize the webdriver with the service and options.
driver = webdriver.Chrome(service=service, options=chrome_options)

#define the path for temporary files 
TempDirPath = rf"{current_directory}\\Frontend\\Files"

#function to set the assistants status  by writing it to a file 
def SetAssistantStatus(status: str):
    with open(rf"{TempDirPath}\Status.data", "w", encoding="utf-8") as file:
        file.write(status)

#function to modify the query to ensure proper punctuation and grammar.
def QueryModifer(query: str):
    new_query =  query.strip().lower()
    query_words = new_query.split()
    question_words = ["how",'what', 'who','where','when','why','which','whose','whom','can you',"what's","where's","how's"]

    #check if the query is a question and add a question mark if it is.
    if any(word + " " in new_query for word in question_words):
        if query_words[-1][-1] in ["?",".","!"]:
            new_query = new_query[:-1]+ "?"
        else:
            new_query += "?"
    else:
        #add a full stop at the end of the query if it doesn't already have one.
        if query_words[-1][-1] in ["?",".","!"]:
            new_query = new_query[:-1]+ "."
        else:
            new_query += "."
    
    return new_query.capitalize()

# function to translate the query to English if it is not in English.
def UniversalTranslator(query: str):
    try:
        #translate the query to English.
        translated_query = mt.translate(query, "en", "auto")
        return translated_query.capitalize()
    except Exception as e:
        print(f"Error in translation: {e}")
        return query
    
#function to perform speech to text conversion.
def SpeechRecognition():
    driver.get("file:///"+Link)
    #start the speech recognition process by clicking the button.
    driver.find_element(by=By.ID, value="start").click()

    while True:
        try:
            #get the text element from the html output element 
            text =  driver.find_element(by=By.ID, value="output").text

            if text:
                #stop recognition by clicking the end button.
                driver.find_element(by=By.ID, value="end").click()

                #if the input language is not English, translate the text to English.
                if InputLanguage.lower() == "en" or "en" in InputLanguage.lower():
                    return QueryModifer(text)
                else:
                    SetAssistantStatus("Translating")
                    return QueryModifer(UniversalTranslator(text))
        
        except Exception as e:
            pass

#the main executions block 
if __name__ == "__main__":
    while True:
        text = SpeechRecognition()
        print(text)