import os
import aiohttp
import requests
from aiogram.utils.markdown import text
import speech_recognition as sr
from dotenv import load_dotenv
from openai import AsyncOpenAI
from PIL import Image
from io import BytesIO
# from hohoho_rupert_bot import bot_name, personage

bot_name = "masterbot"
personage = "Дед Мороз"


help_message = text(
    "/start старт",
    "/help это сообщение",
    "/erase обнулить счетчик",
    "/pic генерация картинки",
    sep="\n"
)

r = sr.Recognizer()
language = 'ru_RU'

png_path = "IMG/newyear_mask.png"
output_path = "IMG/pic.jpg"

load_dotenv()
openai_key = os.getenv("OPENAI_API_KEY")

client = AsyncOpenAI(
    api_key=openai_key
)


def recognise(filename):
    with sr.AudioFile(filename) as source:
        audio_text = r.listen(source)
        try:
            text_r = r.recognize_google(audio_text, language=language)
            return text_r
        except:
            print('Sorry.. run again...')
            return "Sorry.. run again..."


async def picture(content: text, user_id):
    response = await client.images.generate(
        model="dall-e-3",
        prompt="На основании этой темы сделай поздравительную открытку с новым годом, не используй образ санты, "
               "и ВАЖНО!не пиши никаких текстов и букв: " + content,
        size='1024x1024',
        quality="standard",
        n=1,
    )
    image_url = response.data[0].url
    async with aiohttp.ClientSession() as session:
        async with session.get(image_url) as response:
            response_data = await response.read()
    jpg_image = Image.open(BytesIO(response_data))
    png_image = Image.open(png_path)
    if jpg_image.size != png_image.size:
        raise ValueError("Размеры изображений должны совпадать")
    jpg_image.paste(png_image, (0, 0), png_image)
    current_directory = os.getcwd()
    img_folder_path = os.path.join(current_directory, 'IMG')
    name1 = str(user_id)
    name2 = 'pic.jpg'
    name = '_'.join([name1, name2])
    file_path = os.path.join(img_folder_path, name)
    jpg_image.save(file_path, format="JPEG")
    return file_path

    # base_name, ext = os.path.splitext(output_path)
    # counter = 1
    # while os.path.exists(output_path):
    #     output_path_pic = f"{base_name}_{counter}{ext}"
    #     counter += 1
    # jpg_image.save(output_path_pic, format="JPEG")
    # return output_path


file_name_stop_list = "stop_list.txt"
file_name_stop_list = os.path.join(os.getcwd(), "stop_list.txt")
with open(file_name_stop_list, 'r') as file:
    content = file.read()
    stop_list = content.split()


def check_message(content):
    user_words = content.split()
    result = "good"
    for word in user_words:
        if word in stop_list:
            result = "bad_word"
            print("bad_word")
        if len(user_words) > 20:
            result = "too long"
    return result
