from email import message_from_binary_file
from hashlib import new
from pyexpat.errors import messages
import re
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher,FSMContext
from aiogram.utils import executor
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage

import json
import requests
import time


storage = MemoryStorage()

class Form(StatesGroup):
    name = State()
    phone = State()
    company = State()


def auth():
    return False



bot = Bot(token='OOps')
dp = Dispatcher(bot, storage=storage)

new_price = 0


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_1 = "Правила"
    keyboard.add(button_1)

    inline_btn_1 = types.InlineKeyboardButton('Авторизироваться!', callback_data='button1')
    inline_kb1 = types.InlineKeyboardMarkup().add(inline_btn_1)

    await bot.send_message(message.chat.id, "Приветствуем вас в Scrap Price!",reply_markup = keyboard)
    await bot.send_message(message.chat.id, "Нажмите на кнопку, чтобы авторизироваться.", reply_markup= inline_kb1)



@dp.callback_query_handler(text="button1")
async def first_step(call: types.CallbackQuery):
    await bot.answer_callback_query(call.id)
    await call.message.delete()
    print(call.from_user.id)
    if call.from_user.username:
        print(call.from_user.username)
    tgId = {'tgId':str(call.from_user.id)}
    res = requests.post('http://localhost:8000/auth',json=tgId)
    values =  json.loads(res.text)['request']
    if values == 1:
        await call.message.answer("Вы авторизованный пользователь!")
    elif values == 2:
        await call.message.answer("Вы прошли авторизацию!\nДождитесь подтверждения администратора.")
    else:
        await Form.name.set()
        
        await call.message.answer("Вы не авторизованный пользователь!\nВведите свое имя.")


@dp.message_handler(state=Form.name)
async def process_first_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text

    await Form.next()
    await bot.send_message(message.chat.id,'Введите свой номер телефона')    


@dp.message_handler(state=Form.phone)
async def process_phone(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['phone'] = message.text

    await Form.next()
    await bot.send_message(message.chat.id,'Введите компанию, которую вы представляете')


@dp.message_handler(state=Form.company)
async def process_company(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['company'] = message.text
        tgName = ''
        if message.from_user.username:
            tgName = message.from_user.username
        else:
            tgName = "None"
        Jdata2 = {"tgId":message.from_user.id,
        "tgName":tgName,
        "phone":data["phone"],
        "company":data["company"],
        "name":data["name"]
        }
        p = requests.post('http://localhost:8000/reg',json = Jdata2)
        print(p.text) 

    await state.finish()
    await bot.send_message(message.chat.id,'Вы авторизовались.\nЖдите подтверждение администратора')  


@dp.callback_query_handler(text="Auction")
async def first_step(call: types.CallbackQuery):
    global new_price
    # await bot.answer_callback_query(call.id)
    await call.message.delete()
    Jdata2 = {"tgId":str(call.from_user.id)}
    p = requests.post('http://localhost:8000/activateLastAuction',json = Jdata2)
    bid_req = json.loads(p.text)['price']
    new_price = bid_req
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_bids = [f"+1 руб/кг",f"+2 руб/кг",f"+3 руб/кг"]
    button_regulations = "Правила"
    keyboard.add(*button_bids,button_regulations)
    await bot.send_message(call.from_user.id,"Вы учавствуете в аукционе",reply_markup = keyboard)
    

@dp.message_handler()
async def mess(message: types.Message):
    global new_price
    bid = {"bid":0,
        "tgId":message.from_user.id}
    if message.text == "Правила":
        text = open('regulations.txt', encoding='utf8').read()
        await bot.send_message(message.chat.id,text)  
    elif message.text == f"+1 руб/кг":
        new_price += 1
        bid['bid'] = 1
        requests.post('http://localhost:8000/bid',json = bid)
    elif message.text == f"+2 руб/кг":
        new_price += 2
        bid['bid'] = 2
        requests.post('http://localhost:8000/bid',json = bid)
    elif message.text == f"+3 руб/кг":
        new_price += 3
        bid['bid'] = 3
        requests.post('http://localhost:8000/bid',json = bid)
    else:
        await bot.send_message(message.chat.id,'Сообщения отключены. Для повышения ставки, воспользуйтесь кнопками.')
if __name__ == '__main__':
    while True:
        try:
            executor.start_polling(dp, skip_updates=True)
        except:
            time.sleep(3)
