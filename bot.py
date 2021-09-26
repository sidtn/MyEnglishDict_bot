import logging
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.types.message import Message
from aiogram.utils import executor
from config import TOKEN
from val_and_translate import word_validator_and_traslator
from db_manager import DbManage


bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)
db = DbManage('words.db')


@dp.message_handler(commands=['start', 'help'])
async def process_start_command(msg: types.Message):
    await msg.reply('Bot assistant for learning English words.')
    db.add_user(msg.from_user.id)


# @dp.message_handler(commands='test') 
# async def words_trenager()

    

@dp.message_handler()
async def answer_translator(msg: types.Message):
    word_in_db = db.find_word(msg.text.lower().strip())
    if word_in_db:
        await msg.answer(f'{word_in_db[0]} - {word_in_db[1]}')
    else:    
        result = word_validator_and_traslator(msg.text)
        if isinstance(result, str):
            await msg.answer(result)   
        else:
            await msg.answer(f'{result[1]} - {result[0]}') 
            if len(result[1].split(' ')) <= 3: 
                db.add_word(msg.from_user.id, result[1], result[0])  


if __name__ == '__main__':
    executor.start_polling(dp)