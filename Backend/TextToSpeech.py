import pygame 
import random
import asyncio
import edge_tts
import os 
from dotenv import dotenv_values

# Load environment variables from the .env file.
env_vars = dotenv_values(".env")    
AssistantVoice = env_vars.get("AssistantVoice")

#asynchronous function to convert text to audio 
async def TextToAudioFile(text: str):
    file_path = r"Data\speech.mp3"

    if  os.path.exists(file_path):
        os.remove(file_path)

    #create the communicate object to generate speech 
    communicate = edge_tts.Communicate(text, AssistantVoice, pitch="+5Hz", rate="+10%") #type: ignore
    await communicate.save(file_path)

#function to manage text-to-speech playback
def TTS(text , func=lambda r=None:True):
    while True:
        try:
            asyncio.run(TextToAudioFile(text))

            #intialize pygame mixer to play the audio file
            pygame.mixer.init()

            #load the audio file
            pygame.mixer.music.load(r"Data\speech.mp3")
            pygame.mixer.music.play()

            #loop untill the audio is done playing or the function stops 
            while pygame.mixer.music.get_busy():
                if func() == False:
                    break
                pygame.time.Clock().tick(10)

            return True
        
        except Exception as e:
            print(f"An error occurred during text-to-speech conversion: {e}")
            return False    
        
        finally:
            try:
                func(False)
                pygame.mixer.music.stop()
                pygame.mixer.quit()
            except Exception as e:
                print(f"An error occurred while stopping the audio: {e}")

#functions to manage the text-to-speech playback text-to-speech with additional responses for long text 
def TextToSpeech(text: str, func=lambda r=None:True):
    Data = str(text).split(".")

    #list of resposes for cases where the text is too long
    responses = [
        "The rest of the result has been printed to the chat screen, kindly check it out sir.",
        "The rest of the text is now on the chat screen, sir, please check it.",
        "You can see the rest of the text on the chat screen, sir.",
        "The remaining part of the text is now on the chat screen, sir.",
        "Sir, you'll find more text on the chat screen for you to see.",
        "The rest of the answer is now on the chat screen, sir.",
        "Sir, please look at the chat screen, the rest of the answer is there.",
        "You'll find the complete answer on the chat screen, sir.",
        "The next part of the text is on the chat screen, sir.",
        "Sir, please check the chat screen for more information.",
        "There's more text on the chat screen for you, sir.",
        "Sir, take a look at the chat screen for additional text.",
        "You'll find more to read on the chat screen, sir.",
        "Sir, check the chat screen for the rest of the text.",
        "The chat screen has the rest of the text, sir.",
        "There's more to see on the chat screen, sir, please look.",
        "Sir, the chat screen holds the continuation of the text.",
        "You'll find the complete answer on the chat screen, kindly check it out sir.",
        "Please review the chat screen for the rest of the text, sir.",
        "Sir, look at the chat screen for the complete answer."
    ]

    #if the text is very long (more than 4senctences and 250 characters),add a responses messages 
    if len(Data) > 4 or len(text) >= 250:
        TTS(' '.join(text.split('.')[0:2])+'.'+ random.choice(responses), func)
    else:
        TTS(text,func)

#main execution loop 
if __name__ == "__main__":
    while True:
        TextToSpeech(input('enter your text: '))