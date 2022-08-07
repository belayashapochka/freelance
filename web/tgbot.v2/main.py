from flask import Flask, request, make_response, render_template, redirect
from threading import Thread
from database.ormHandler import insertTgUser,checkAuth,userInfo,updateIsAuth,insertAuction,getAuction,getAuthUser,deleteAuction,activateLastAuction,changeAuctionPrice,checkAuctionWinner,auctionBegin,isUserAuction,resetAuctionStatus,getAllAuctionUser,resetAuction,getByTgId,insertRate,sortByTimeRate

import telebot
import os
import codecs

import time as t
import datetime as d

bot = telebot.TeleBot(token='OOps')

UPLOAD_FOLDER = './upload'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

winner = ''

auction_start = False
auction_end = False
gif_link = ''
photo_link = ''


def timerPing(time_before_start):
    global auction_start
    end_time = time_before_start*60 + int(t.time())
    users = getAuthUser()
    while True:
        time = int(t.time())
        #TIMEEEEEEEEEEEEEEEEEEEEEEEEE
        if end_time - time == 60*60:
            for user in users:
                bot.send_message(int(user.tgId),'До начала аукциона остался 1 час',parse_mode= "Markdown")
            t.sleep(1)
        elif end_time - time == 30*60:
            for user in users:
                bot.send_message(int(user.tgId),'До начала аукциона осталось 30 минут',parse_mode= "Markdown")
            t.sleep(1)
        elif end_time - time == 5*60:
            for user in users:
                bot.send_message(int(user.tgId),'До начала аукциона осталось 5 минут',parse_mode= "Markdown")
            t.sleep(1)
        elif end_time-time < 0 or auction_start:
            auction_start = False
            print('sdsd')
            print(auction_start)
            return True
        else:
            pass


def timeHalper(in_t):
    input_minute = int(in_t[8]+in_t[9])*24*60 + int(in_t[11]+in_t[12])*60 + int(in_t[14]+in_t[15])
    te = d.datetime.now()
    d_now = te.day
    h_now = te.hour
    m_now = te.minute
    time_different_minute = input_minute - (d_now*24*60+h_now*60+m_now)
    print(d_now,h_now,m_now)
    print(time_different_minute)
    return  time_different_minute


def timeAuction(user_time):
    global winner,auction_end,gif_link,photo_link
    end_time = user_time + int(t.time())
    while True:
        collect = getAllAuctionUser()
        time = int(t.time())
        auctions = getAuction()
        auction = auctions[len(auctions)-1]
        if end_time-time == 600:

            for user in collect:
                bot.send_message(int(user.tgId),'До окончания аукциона осталось 10 минут',parse_mode= "Markdown")
            t.sleep(1)
        elif end_time-time < 0 or auction_end:
            auction_end = False
            resetAuction(winner,auction.auctionId)
            resetAuctionStatus()
            keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            button_1 = "Правила"
            keyboard.add(button_1)
            for user in collect:
                print(photo_link,gif_link)
                if auction.sendGif:
                    bot.send_video(int(user.tgId),gif_link) 
                if auction.sendPhoto:
                    bot.send_photo(int(user.tgId),photo_link)
                if str(user.tgId) == str(winner):
                    bot.send_message(int(user.tgId),f'🏆 Поздравляем! Ваша ставка победила в аукционе. Мы с вами свяжемся в ближайшее время.',parse_mode= "Markdown",reply_markup=keyboard)
                else:
                    bot.send_message(int(user.tgId),f'Торги закончены. Победил другой участник. Лучшее предложение от участника {collect.index(user) + 1} *{auction.price} руб/кг.*',parse_mode= "Markdown",reply_markup=keyboard)
            return True
        else:
            pass


def send_photo(tgId):
    photos = []
    files = os.listdir(os.path.join(app.config['UPLOAD_FOLDER']))
    auctions = getAuction()
    auction = auctions[len(auctions)-1]
    date_start = d.datetime.fromisoformat(auction.timeStart)
    date_end = date_start + d.timedelta(minutes=auction.timeDelay)
    for file in files:
        path = os.path.join(os.path.abspath(app.config['UPLOAD_FOLDER']), file)
        if files.index(file)==0:
            photos.append(telebot.types.InputMediaPhoto(open(path,'rb'),caption=f"🏆 Аукцион #{auction.auctionId}\n\nЛот:* {auction.title}*\nВес: *{auction.weight}* кг\n\nОписание: {auction.description}\n\n{auction.payType} \n\nСтарт аукциона: {date_start.strftime('%H:%M %Y-%m-%d')}\nОкончание аукциона: {date_end.strftime('%H:%M %Y-%m-%d')}",parse_mode= "Markdown"))
        else:
            photos.append(telebot.types.InputMediaPhoto(open(path,'rb')))
    bot.send_media_group(int(tgId), photos, timeout = 120)
    bot.send_message(int(tgId),f"❗️ Стартовая цена: {auction.price} руб/кг")


def informingNewUsers(id,auction):
    if checkAuctionWinner(auction.auctionId) == 1:
        send_photo(id)
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("Учавствовать в аукционе", callback_data="Auction"))
        bot.send_message(int(id),'Торги открыты, предлагайте вашу цену. Желаем удачи!',reply_markup=markup)
    elif checkAuctionWinner(auction.auctionId) == 0:
        send_photo(id)


@app.route("/ping")
def ping():
    auction = getAuction()
    for auc in auction:
        print(auc.auctionId)

    return '12'


@app.route("/reg", methods = ['POST'])
def registration():
    data = request.get_json()
    try:
        insertTgUser(tgId=data['tgId'],
                        tgName=data['tgName'],
                        phone=data['phone'],
                        company=data['company'],
                        name=data['name'])

        return make_response({
    "status":"200",
    "request":"OK"})
    except Exception:
        print(Exception)
        return "Something went wrong"


@app.route("/auth", methods = ['POST'])
def auth():
    data = request.get_json()
    check_auth =  checkAuth(tgId=data['tgId'])
    return make_response({
        "status":"200",
        "request":check_auth})


@app.route("/")
@app.route("/main")
def index():
    return render_template('main.html')


@app.route("/users")        
@app.route("/users/<id>")
def users(id=None):
    global bot
    if id:
        auctions = getAuction()
        
        updateIsAuth(id)
        bot.send_message(int(id),'Администратор подтвердил ваш профиль. Теперь вы авторизованый пользователь.\nДождитесь аукциона!')
        if len(auctions) != 0:
            auction = auctions[len(auctions)-1]
            informingNewUsers(id,auction)
        return redirect('/users')
    collection = userInfo()
    return render_template('users.html',collection_users=collection)


@app.route('/auction_create', methods=['GET', 'POST'])
def upload_file():
    global winner,auction_end,auction_start
    auction = getAuction()
    users = getAllAuctionUser()
    if request.method == 'POST':
        # print(request.files)
        auction_start = False
        auction_end = False
        winner = ''
        if 'file1' not in request.files:
            return 'there is no file1 in form!'

        files = os.listdir(os.path.join(app.config['UPLOAD_FOLDER']))
        for file in files:
            path = os.path.join(os.path.abspath(app.config['UPLOAD_FOLDER']), file)
            os.remove(path)

        for file in request.files:
            # print(file)
            try:
                file1 = request.files[file]
                path = os.path.join(app.config['UPLOAD_FOLDER'], file1.filename)
                file1.save(path)
            except:
                continue
        deleteAuction(auction[0].auctionId) if len(auction)==3 else 5+4
        form_dict = request.form.to_dict()
        insertAuction(title=form_dict['title'],
        auctionId=auction[len(auction)-1].auctionId + 1 if auction else 1,
        description=form_dict['description'],
        weight=form_dict['weight'],
        price=form_dict['price'],
        timeStart=form_dict['date'],
        timeDelay=form_dict['time'],
        payType=form_dict['payType'],
        sendGif = True if 'gif' in form_dict.keys() else False,
        sendPhoto = True if 'photo' in form_dict.keys() else False)
        
        print ('gif' in form_dict.keys())
        global bot
        collect_users = getAuthUser()


        for user in collect_users:            
            
            send_photo(user.tgId)

        timer_ping = Thread(target=timerPing,args=(timeHalper(request.form['date']),))
        timer_ping.start()
        return redirect('/auction_create')
    return render_template('create_auction.html',auction=auction[len(auction)-1] if auction else auction,collection_users=users)


@app.route("/ping_auction")
def pingAuction():
    global bot,auction_start
    auction_start = True
    collect = getAuthUser()
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("Учавствовать в аукционе", callback_data="Auction"))

    auctionBegin(getAuction()[len(getAuction()) - 1])
    resetAuctionStatus()
    for user in collect:
        bot.send_message(int(user.tgId),'Торги открыты, предлагайте вашу цену. Желаем удачи!',reply_markup=markup)
    auction = getAuction()

    time_auction = Thread(target=timeAuction,args=(auction[len(auction)-1].timeDelay * 60,))
    time_auction.start()

    return redirect('/auction_create')   


@app.route("/activateLastAuction", methods = ['POST'])
def activate():
    data = request.get_json()
    try:
        activateLastAuction(data['tgId'])
        auctions = getAuction()
        auction = auctions[len(auctions)-1]
        collect = getAllAuctionUser()
        for user in collect:
            bot.send_message(int(user.tgId),f'Новый участник в аукционе.\nВсего участников {len(collect)}')
        
        
        return make_response({
            "status":"200",
            "price":auction.price,
            "request":"OK"})
    except Exception:
        print(Exception)
        return make_response({
        "status":"500",
        "request":"Something went wrong"})


@app.route('/bid', methods=['POST'])
def bid():
    global winner,bot
    j = request.get_json()
    auctions = getAuction()
    auction = auctions[len(auctions) - 1]
    if checkAuctionWinner(auction.auctionId) == 1:
        if isUserAuction(str(j['tgId'])):
            new_price = auction.price + j['bid']
            if changeAuctionPrice(new_price,auction.auctionId):
                winner = j['tgId']
                collect = getAllAuctionUser()
                for user in collect:
                    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
                    button_bids = [f"+1 руб/кг",f"+2 руб/кг",f"+3 руб/кг"]
                    button_regulations = "Правила"
                    keyboard.add(*button_bids,button_regulations)
                    if str(winner) != str(user.tgId):
                        bot.send_message(int(user.tgId),f'Новая ставка участника {collect.index(user) + 1}: {new_price} рублей',reply_markup=keyboard)
                    else:
                        bot.send_message(int(user.tgId),f'Ваша ставка: {new_price} рублей',reply_markup=keyboard)
                company = getByTgId(j['tgId']).company
                insertRate(
                    company=company,
                    bet=new_price,
                    auctionId=auction.auctionId
                )
                return make_response({
                    "status":"200",
                    "request":"saved successfully"})  
        else:
            bot.send_message(int(j['tgId']),'Вы не учавствуете в аукционе.')
            return make_response({
                    "status":"200",
                    "request":"Еhe user is not participating in the auction"})            
    else:
        bot.send_message(int(j['tgId']),'Торги закончены. Дождитесь нового аукциона')
        return make_response({
                "status":"200",
                "request":"Auction not begined"})


@app.route("/auctions")
def auctions():
    auctions = getAuction()
    auction =[]
    for win in auctions:
        auction.append([win,getByTgId(win.winner) ])
    return render_template('auctions.html',collection_auctions=auction)


@app.route("/bids/<auctionId>")
def bids(auctionId):
    bids = sortByTimeRate(auctionId=auctionId)
    return render_template('bids.html',bids=bids,auctionId=auctionId)


@app.route("/auction_end")
def auctionEnd():
    global auction_end 
    print('sdddssdds')
    auction_end = True
    return redirect('/auction_create')


@app.route('/regulations',methods=['GET', 'POST'])
def regulations():
    if request.method == 'POST':
        text_regulations = request.form['text_regulations']
        print(text_regulations)
        file = codecs.open('../../bot/regulations.txt','w','utf-8')
        file.write(text_regulations)
        file.close()
    text_regulations = open('../../bot/regulations.txt',encoding='utf8').read()
    return render_template('regulations.html',text_regulations=text_regulations)


@app.route('/media',methods=['GET', 'POST'])
def media():
    global gif_link,photo_link
    if request.method == 'POST':
        form_dict = request.form.to_dict()
        gif_link = form_dict['gif']
        photo_link = form_dict['photo']
    return render_template('media.html')


if __name__ == '__main__':  
    app.run(host="localhost", port=8000, debug=True)
