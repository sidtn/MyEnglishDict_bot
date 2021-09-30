import logging
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils.exceptions import ButtonDataInvalid
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
from aiogram.dispatcher.filters.state import State, StatesGroup
from config import TOKEN, ADMIN_ID
from val_and_translate import word_validator_and_traslator
from db_manager import DbManage
import os


storage = MemoryStorage()
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=storage)
logging.basicConfig(level=logging.INFO)
db = DbManage('words.db')
ALLOWED_USERS = db.get_users()


class Form(StatesGroup):
    name = State()


@dp.message_handler(commands=['start', 'help'])
async def process_start_command(msg: types.Message):
    await msg.reply(f'Hi {msg.from_user.username}.\n'
                     'This is a bot assistant for learning English words.\n'
                     'List of available commands:\n'
                     '/test - training the words of all users;\n'
                     '/mytest - training the words from your dictionaty;\n'
                     '/del - shows a list of the last 5 words with buttons for delete;\n'
                     '/f and verb - shows irregular verb forms;\n'
                     '/g and verb - shows infinitive or gerund to be used after the verb;\n'
                     '<b>For registration send any text to the bot.</b>', 
                     parse_mode=types.ParseMode.HTML)


@dp.callback_query_handler(lambda c: c.data.startswith('request_'))
async def user_request(call: types.CallbackQuery):
    await call.answer()
    await bot.delete_message(call.from_user.id, message_id=call.message.message_id)
    await bot.send_message(call.from_user.id, 'The admin has received your message.')
    newuser = call.data.split('_')[1:]
    keyboard = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton('Add this user', callback_data=f'adduser_{newuser[0]}')
    keyboard.add(button)
    await bot.send_message(ADMIN_ID, f'User {newuser[1]} want to join.', reply_markup=keyboard)


@dp.callback_query_handler(lambda c: c.data.startswith('adduser_'))
async def add_user(call: types.CallbackQuery):
    await call.answer()
    user_id = int(call.data.split('_')[1])
    db.add_user(user_id)
    global ALLOWED_USERS
    ALLOWED_USERS = db.get_users()
    await bot.delete_message(call.from_user.id, message_id=call.message.message_id)
    await bot.send_message(call.from_user.id, f'The user with id {user_id} has been added.')
    await bot.send_message(user_id, 'Yor request is approved. You can use the bot')


@dp.callback_query_handler(lambda c: c.data.startswith('test_'))
async def check_answer(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    answer = call.data.split('_')[1:]
    if answer[0].replace('@', ' ') != answer[1].replace('@', ' '):
        await call.message.answer('Wrong')
    else:
        await call.message.answer('Correct')
        try:
            async with state.proxy() as data:
                msg = data['name']
                await words_trenager(msg, state)
        except ButtonDataInvalid:
            await call.message.answer('Sending error, click again')


@dp.callback_query_handler(lambda c: c.data.startswith('del_'))
async def check_answer(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    word_for_delete = call.data.split('_')[1]
    db.del_record(word_for_delete)
    os.remove(f'words_audio/{word_for_delete}.mp3')
    await call.message.answer(f'Record [{word_for_delete}] was deleted')
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)


@dp.message_handler(commands='del')
async def delere_words(msg: types.Message):
    user_id = msg.from_user.id
    words = db.get_words_for_delete(user_id)
    if words:
        for word in reversed(words):
            keyboard = types.InlineKeyboardMarkup()
            button = types.InlineKeyboardButton('Delete', callback_data=f'del_{word[0]}')
            keyboard.add(button)
            await msg.answer(f'{word[0]} - {word[1]}', reply_markup=keyboard)
    else:
        await msg.answer("You don't have any words to delete.")


@dp.message_handler(commands=['test', 'mytest'])
async def words_trenager(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = msg
    if msg.text == '/test':
        testdata = db.get_word_for_test()
        from_dict = ''
    else:
        testdata = db.get_word_for_test(for_user=msg.from_user.id)
        from_dict = f'[{msg.from_user.username}]'
    if testdata:
        variants = list(map(lambda x: x.replace(' ', '@'), testdata[1]))
        correct_answer = testdata[0][1].replace(' ', '@')
        keboard = types.InlineKeyboardMarkup(row_width=2)
        buttons_list = []
        for word in variants:
            callback_data = f'test_{word}_{correct_answer}'
            if len(callback_data.encode('utf-8')) > 62:
                callback_data = f'test_{word[0:5]}_{correct_answer[0:5]}'
            button = types.InlineKeyboardButton(word.replace('@', ' '), callback_data=callback_data)
            buttons_list.append(button)
        keboard.add(buttons_list[0], buttons_list[1])
        keboard.add(buttons_list[2], buttons_list[3])
        audio = open(f'words_audio/{testdata[0][0]}.mp3', 'rb')
        await bot.send_voice(msg.from_user.id, voice=audio, 
                             caption=f"<b>{testdata[0][0]}</b>{' '*10}<i>{from_dict}</i>", 
                             reply_markup=keboard, 
                             parse_mode=types.ParseMode.HTML)
    else:
        await msg.answer("There no the words for testing")


@dp.message_handler(lambda msg: msg.text.startswith('/f'))
async def show_irregular_verbs(msg: types.Message):
    msg_text = msg.text.lstrip('/f').strip()
    verb_forms = db.get_irregular_vebs(msg_text)
    if verb_forms:
        await msg.answer(f'<b>{verb_forms[4]}</b>\n{verb_forms[1]}\n{verb_forms[2]}\n{verb_forms[3]}',
                         parse_mode=types.ParseMode.HTML)
    else:
        await msg.answer(f'Word [{msg_text}] not found.')


@dp.message_handler(lambda msg: msg.text.startswith('/g'))
async def show_gerund_or_inf(msg: types.Message):
    msg_text = msg.text.lstrip('/g').strip()
    result = db.get_data_from_verbs(msg_text)
    if result:
        await msg.answer(f'<b>{result[1]}</b> is used after the word <b>"{result[0]}"</b>',
                         parse_mode=types.ParseMode.HTML)
    else:
        await msg.answer(f'Word [{msg_text}] not found.')


@dp.message_handler(lambda msg: msg.from_user.id in ALLOWED_USERS)
async def answer_translator(msg: types.Message):
    word_in_db_user = db.find_word(msg.text.lower().strip(), msg.from_user.id)
    word_in_db_all = db.find_word(msg.text.lower().strip())
    if word_in_db_user:
        audio = open(f'words_audio/{word_in_db_user[0]}.mp3', 'rb')
        await bot.send_voice(msg.from_user.id, voice=audio, caption=f'{word_in_db_user[0]} - {word_in_db_user[1]}')
    elif word_in_db_all:
        audio = open(f'words_audio/{word_in_db_all[0]}.mp3', 'rb')
        await bot.send_voice(msg.from_user.id, voice=audio, caption=f'{word_in_db_all[0]} - {word_in_db_all[1]}')
        db.add_word(msg.from_user.id, word_in_db_all[0], word_in_db_all[1])
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


@dp.message_handler()
async def input_from_unregistered_user(msg: types.Message):
    if msg.from_user.id not in ALLOWED_USERS:
        keyboard = types.InlineKeyboardMarkup()
        button = types.InlineKeyboardButton('Click', callback_data=f'request_{str(msg.from_user.id)}_{msg.from_user.username}')
        keyboard.add(button)
        await msg.answer("If you want to translate and add words to the you dictionary, click on the button,"
                         "and admin will receive your request.", reply_markup=keyboard)


if __name__ == '__main__':
    executor.start_polling(dp)
