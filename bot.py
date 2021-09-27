import logging
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils.exceptions import ButtonDataInvalid
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
from aiogram.utils.exceptions import ButtonDataInvalid
from aiogram.dispatcher.filters.state import State, StatesGroup
from config import TOKEN, ALLOWED_USERS, ADMIN_ID
from val_and_translate import word_validator_and_traslator
from db_manager import DbManage
import os


storage = MemoryStorage()
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=storage)
logging.basicConfig(level=logging.INFO)
db = DbManage('words.db')

class Form(StatesGroup):
    name = State()  


@dp.message_handler(commands=['start', 'help'])
async def process_start_command(msg: types.Message):
    keyboard = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton('Click', callback_data=f'?request?{str(msg.from_user.id)}_{msg.from_user.username}')
    keyboard.add(button)
    await msg.answer("Bot assistant for learning English words." 
                    "If you want to use the bot, tup it, and admin will receive your request.", reply_markup=keyboard)
    

@dp.callback_query_handler(lambda c: c.data.startswith('?request?'))
async def user_request(call: types.CallbackQuery):
    await call.answer()
    await bot.delete_message(call.from_user.id, message_id=call.message.message_id)
    await bot.send_message(call.from_user.id, 'The admin has received your message.')
    newuser = call.data.lstrip('?request?').split('_')
    keyboard = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton('Add this user', callback_data=f'?adduser?{newuser[0]}')
    keyboard.add(button)
    await bot.send_message(ADMIN_ID, f'User {newuser[1]} want to join.', reply_markup=keyboard)


@dp.callback_query_handler(lambda c: c.data.startswith('?adduser?'))  
async def add_user(call: types.CallbackQuery):
    await call.answer()
    user_id = int(call.data.lstrip('?adduser?'))
    db.add_user(user_id)
    await bot.delete_message(call.from_user.id, message_id=call.message.message_id)
    await bot.send_message(call.from_user.id, f'The user with id {user_id} has been added.')


@dp.message_handler(commands='del')
async def delere_words(msg: types.Message):
    user_id = msg.from_user.id  
    words = db.get_words_for_delete(user_id)
    for word in reversed(words):
        keyboard = types.InlineKeyboardMarkup()
        button = types.InlineKeyboardButton('Delete', callback_data=f'?del?{word[0]}')
        keyboard.add(button)
        await msg.answer(f'{word[0]} - {word[1]}', reply_markup=keyboard)


@dp.message_handler(commands='test') 
async def words_trenager(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = msg
    testdata = db.get_word_for_test()
    keboard = types.InlineKeyboardMarkup(row_width=2)
    buttons_list = []
    for word in testdata[1]:
        button = types.InlineKeyboardButton(word, callback_data=f'?test?{word}_{testdata[0][1]}')
        buttons_list.append(button)
    keboard.add(buttons_list[0], buttons_list[1]) 
    keboard.add(buttons_list[2], buttons_list[3])
    audio = open(f'words_audio/{testdata[0][0]}.mp3', 'rb')
    await bot.send_voice(msg.from_user.id, voice=audio, caption=testdata[0][0], reply_markup=keboard)
    

@dp.message_handler(lambda msg: msg.from_user.id in ALLOWED_USERS)
async def answer_translator(msg: types.Message):
    word_in_db = db.find_word(msg.text.lower().strip())
    if word_in_db:
        audio = open(f'words_audio/{word_in_db[0]}.mp3', 'rb')
        await bot.send_voice(msg.from_user.id, voice=audio, caption=f'{word_in_db[0]} - {word_in_db[1]}')
    else:    
        result = word_validator_and_traslator(msg.text)
        if isinstance(result, str):
            await msg.answer(result)   
        else:
            if len(result[1].split(' ')) <= 3: 
                db.add_word(msg.from_user.id, result[1], result[0]) 
                audio = open(f'words_audio/{result[1]}.mp3', 'rb')
                await bot.send_voice(msg.from_user.id, voice=audio, caption=f'{result[1]} - {result[0]}') 
            else:
                await msg.answer(f'{result[1]} - {result[0]}')    


@dp.callback_query_handler(lambda c: c.data.startswith('?test?'))  
async def check_answer(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    answer = call.data.lstrip('?test?').split('_')
    if answer[0] != answer[1]:
        await call.message.answer('Wrong')
    else:
        await call.message.answer('Correct') 
        try:
            async with state.proxy() as data:
                msg = data['name'] 
                await words_trenager(msg, state)
        except ButtonDataInvalid:
            await call.message.answer('Sending error, click again')    


@dp.callback_query_handler(lambda c: c.data.startswith('?del?'))  
async def check_answer(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    word_for_delit = call.data.lstrip('?del?')
    db.del_record(word_for_delit)
    os.remove(f'words_audio/{word_for_delit}.mp3')
    await call.message.answer(f'Record [{word_for_delit}] was deleted')
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)

            
if __name__ == '__main__':
    executor.start_polling(dp)