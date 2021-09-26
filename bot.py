import logging
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils.exceptions import ButtonDataInvalid
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
from aiogram.dispatcher.filters.state import State, StatesGroup
from config import TOKEN
from val_and_translate import word_validator_and_traslator
from db_manager import DbManage


storage = MemoryStorage()
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=storage)
logging.basicConfig(level=logging.INFO)
db = DbManage('words.db')

class Form(StatesGroup):
    name = State()  


@dp.message_handler(commands=['start', 'help'])
async def process_start_command(msg: types.Message, ):
    await msg.reply('Bot assistant for learning English words.')
    db.add_user(msg.from_user.id)


@dp.message_handler(commands='test') 
async def words_trenager(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = msg
    testdata = db.get_word_for_test()
    keboard = types.InlineKeyboardMarkup(row_width=2)
    buttons_list = []
    for word in testdata[1]:
        button = types.InlineKeyboardButton(word, callback_data=f'{word}_{testdata[0][1]}')
        buttons_list.append(button)
    keboard.add(buttons_list[0], buttons_list[1]) 
    keboard.add(buttons_list[2], buttons_list[3])
    await msg.answer(testdata[0][0], reply_markup=keboard)


@dp.callback_query_handler(lambda c: c.data)  
async def check_answer(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    answer = call.data.split('_')
    if answer[0] != answer[1]:
        await call.message.answer('Wrong')
    else:
        await call.message.answer('Correct') 
        async with state.proxy() as data:
            msg = data['name'] 
            await words_trenager(msg, state)


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