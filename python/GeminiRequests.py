
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



# given a string containing the URL of an image, return the image in a form that can sent to gemini
def urlToImage(url):
    image_bytes = requests.get(url).content
    image_part = types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")
    return image_part


# requests description of the image from gemini. returns an html file or smth
def getDescription(img):
    chat.send_message(img)

    prompt = "Describe these characteristics: CATEGORY, COLOR, BRAND OR TYPE," \
    " DISTINCTIVE FEATURE of the object in the image in exactly one word each," \
    " except for DISTINCTIVE FEATURE, which is three words. Your response" \
    " should be exactly 6 words long, with each characteristic separated by a comma"

    response = chat.send_message(prompt)
    return response


# given a description of an object, return an embedding of that description,
# such that it can easily be compared to other possible descriptions
def generateEmbedding(str):
    result = client.models.embed_content(
                model="gemini-embedding-2",
                contents = str,
                config=types.EmbedContentConfig(output_dimensionality=768)
            )
    return result


# start execution here
# asks the user to input a url. returns a 768-dimension embedding of the description of the image at the url

def main():
    url = input("Enter the url of an image: ")
    print(url)
    img = urlToImage(url)
    description = getDescription(img).text
    print(description)
    embedding = generateEmbedding(description)
    print(embedding)
    return embedding


if __name__ == "__main__":
    main()

