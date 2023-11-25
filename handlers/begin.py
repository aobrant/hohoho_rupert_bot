import os
from aiogram import Router, types, F
from aiogram.types import FSInputFile
from openai import AsyncOpenAI
from aiogram.filters import Command
from dotenv import load_dotenv
from misc import help_message, picture, check_message
from sql_intergrate import get_or_create_user, increase_counter, update_prompt, get_prompt
from misc import bot_name, personage

router = Router()
load_dotenv()
openai_key = os.getenv("OPENAI_API_KEY")

language = 'ru'


@router.message(Command("start"))
async def process_start_command(message: types.Message):
    await message.answer(" Хо - хо - хо, как себя вели в этом году, детишки? Хорошо? ❄️❄️⛄️❄️❄️")


@router.message(Command("help"))
async def process_help_command(message: types.Message):
    await message.answer(help_message)


client = AsyncOpenAI(
    api_key=openai_key
)


@router.message(Command("pic"))
async def pic_test(message: types.Message):
    user_id = message.from_user.id
    content = "Веселый новый год"
    filepath = await picture(content, user_id)
    cat = FSInputFile(filepath)
    await message.answer_photo(cat)
    try:
        os.remove(filepath)
    except FileNotFoundError:
        print(f"Файл {filepath} не найден.")
    except Exception as e:
        print(f"Произошла ошибка при удалении файла: {str(e)}")


@router.message(F.text)
async def message_response(message: types.Message):
    user_id = message.from_user.id
    user = get_or_create_user(user_id, bot_name)
    counter = user.counter
    if counter < 20:
        counter += 1
        user_text = message.text
        message_status = check_message(user_text)
        if message_status == "good":
            increase_counter(user_id)
            old_prompt = get_prompt(user_id)
            prompt = "Ты " + personage + ", настоящий, все по канону. На все вопросы отвечаешь, как если бы ты был " \
                     "им. Важно — тебе могут писать дети,и ты обязан соблюдать возрастное " \
                     "ограничение PG-13. Стараешься давать им добрые, хорошие советы и пожелания, " \
                     "даже если они пишут грубости. Прредыдущий разговор был такой '" + old_prompt + \
                     "', учти это но на старые вопросы не отвыечай, а теперь отвечай  на новый вопрос с учетом предыдущего диалого. Новый вопрос " + user_text

            chat_completion = await client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model="gpt-3.5-turbo",
            )
            gpt_reply = chat_completion.choices[0].message.content
            update_prompt(user_id, user_text)
            await message.answer(gpt_reply)
        elif message_status == "bad_word":
            increase_counter(user_id)
            text = "Не ругайся, маленький шалунишка"
            await message.answer(text)
        elif message_status == "too long":
            text = "Охохо, ты совсем запутал старенького дедушку, давай покороче"
            await message.answer(text)
            increase_counter(user_id)
        else:
            await message.answer("Чтото пошло не так")
            increase_counter(user_id)
    elif counter == 20:
        text = "Ну вот и поговорили достаточно. Время идти дальше, столько дел перед праздниками!"
        old_prompt = get_prompt(user_id)
        content = "Ты " + personage + ", настоящий, все по канону. Предыдущие темы разговора'"+ old_prompt + "' Возьми из них основные три темы волнующие собеседника и нарисуй на основании их картинку"
        filepath = await picture(content, user_id)
        cat = FSInputFile(filepath)
        await message.answer_photo(cat)
        try:
            os.remove(filepath)
        except FileNotFoundError:
            print(f"Файл {filepath} не найден.")
        except Exception as e:
            print(f"Произошла ошибка при удалении файла: {str(e)}")
        await message.answer(text)
        increase_counter(user_id)
    else:
        increase_counter(user_id)
        message.answer("С Новым Годом мой маленький друг")
