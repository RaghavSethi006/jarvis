import asyncio
from random import randint 
from PIL import Image 
from aiohttp import Payload
import requests 
from dotenv import get_key
import os 
from time import sleep 

#Function to open and display images based on a given promt 
def open_images(promt):
    folder_path = r"Data"
    promt = promt.replace(' ','_')

    #genereate the filenames for the images
    Files = [f"{promt}{i}.jpg" for i in range(1,5)]

    for jpg_file in Files:
        image_path = os.path.join(folder_path,jpg_file)

        try:
            #try to open and display the image 
            img = Image.open(image_path)
            print(f"opening image: {image_path}")
            img.show()
            sleep(1)
        
        except IOError:
            print(f'unable to open {image_path}')

#API deatils for the hugging face stable diffusion 
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
Headers = {"Authorization": f"Bearer {get_key('.env', 'HuggingFaceAPIKey')}"} 

#Async function to send a query to the hugging face API
async def query(payload):
    response = await asyncio.to_thread(requests.post,API_URL,headers = Headers, json=payload)
    return response.content

#Async function to generate images based on the given promt 
async def generate_images(promt : str):
    tasks = []

    #Create 4images tasks
    for _ in range(4):
        payload = {
            "inputs" : f"{promt}, quality=4K , sharpness=maximum, Ultra High deails , high resolution, seed ={randint(0,1000000)}"
        }
        task =asyncio.create_task(query(payload))
        tasks.append(task)

    #wait for all task to complete 
    image_bytes_list = await asyncio.gather(*tasks)

    #save the generated images to files 
    for i , image_bytes in enumerate(image_bytes_list):
        with open(fr"Data\{promt.replace(' ','_')}{i+1}.jpg",'wb') as f:
            f.write(image_bytes)

#wraper function to generate and open images 
def GenerateImages(promt:str):
    asyncio.run(generate_images(promt))
    open_images(promt)

#main loop to monitor for image generation requests
while True:

    try:
        #read the status and promt from the data files 
        with open(r"Frontend\Files\ImageGeneration.data","r") as f:
            Data: str = f.read()

        Promt,Status = Data.split(",")

        #if the status indicates   an image generation requests 
        if Status == "True":
            print("generating images...")
            ImagesStatus= GenerateImages(promt=Promt) 

            #reset the status  in the fie after generation images 
            with open(r"Frontend\Files\ImageGeneration.data","w") as f:
                f.write("False,False")
                break
        
        else:
            sleep(1)

    except :
        pass
        