
import requests
from google import genai
from google.genai import types
import os
from dotenv import load_dotenv

load_dotenv(override=True)
key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key = key)

chat = client.chats.create(
    model= "gemini-3.5-flash-lite",
)
response = chat.send_message("Hello")

print(response.text)

image_bytes = requests.get("https://hips.hearstapps.com/clv.h-cdn.co/assets/16/18/gettyimages-586890581.jpg?crop=0.668xw:1.00xh;0.219xw,0").content
image_part = types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")




# requests description of the image from gemini. returns an html file or smth
def getDescription(img):
    chat.send_message(image_part)

    prompt = "Describe these characteristics: CATEGORY, COLOR, BRAND OR TYPE," \
    " DISTINCTIVE FEATURE of the object in the image in exactly one word each," \
    " except for DISTINCTIVE FEATURE, which is three words. Your response" \
    " should be exactly 6 words long, with each characteristic separated by a comma"

    response = chat.send_message(prompt)
    return response

toPrint = getDescription(image_part)

print(toPrint.text)

