from database.model import *
import datetime

def insertTgUser(tgId,name, tgName, phone, company=''):
    with db:
        temp = UserTg(tgId=tgId,
               name=name,
               tgName=tgName,
               phone=phone,
               company=company,
               isAuth=False,
               lastAuction=False)
        temp.save()
    print('DONE inserting TgUser')

def getAllUsers():
    with db:
        dict=[]
        for user in UserTg.select():
            dict.append(user.tgName)
    print('DONE Selecting')
    return dict

def isAuth(TgName):
    with db:
        try:
            user = UserTg.get(UserTg.tgName == TgName)
            return True
        except DoesNotExist:
            return False

def userInfo():
    collection =[]
    with db:
        for user in UserTg.select().order_by(-UserTg.id):
            '''user.firstName,
              user.lastName,
              user.tgName,
              user.phone,
              user.company,
              user.isAuth,
              user.lastAuction
             '''
            collection.append(user)
    return collection

def getAuthUser():
    collection=[]
    with db:
        for user in UserTg.select().where(UserTg.isAuth == True):
            collection.append(user)
    return collection

def checkAuth(tgId):
    with db:
        try:
            user = UserTg.get(UserTg.tgId == tgId)
            if user.isAuth == True:
                return 1
            else:
                return 2
        except DoesNotExist:
            return 3

def getByTgId(tgId):
    with db:
        try:
            user = UserTg.get(UserTg.tgId == tgId)
            return user
        except DoesNotExist:
            return False

def updateIsAuth(tgId):
    with db:
        try:
            user = UserTg.get(UserTg.tgId == tgId)
            user.isAuth = True
            user.save()
            return True
        except DoesNotExist:
            return False

def insertAuction(title,weight,auctionId,description,price,timeStart,timeDelay,payType,sendGif,sendPhoto,winner='None'):
    with db:
        temp = Auction(title=title,
               auctionId=auctionId,
               description=description,
               weight=weight,
               price=price,
               timeStart=timeStart,
               timeDelay=timeDelay,
               payType=payType,
               sendPhoto=sendPhoto,
               sendGif = sendGif,
               winner=winner)
        try:
            temp.save()
            print('DONE inserting Auction')
        except:
            print('Something went wrong!')

def changeAuctionStatus(tgId):
    try:
        user = UserTg.get(UserTg.tgId == tgId)
        user.lastAuction=True
        user.save()
    except DoesNotExist:
        print("Something went wrong!")
        return False

def resetAuctionStatus():
    with db:
        try:
            for user in UserTg.select():
                user.lastAuction = False
                user.save()
            print('DONE Reseting')
        except:
            print('Somthing went wrong')

def getAuction():
    with db:
        try:
            auction = []
            for auc in Auction.select():
                auction.append(auc)
            return auction 
        except:
            print('Somthing went wrong')

def activateLastAuction(tgId):
    with db:
        try:
            user = UserTg.get(UserTg.tgId == tgId)
            user.lastAuction = True
            user.save()
            print("Change is done")
            return True
        except DoesNotExist:
            print("Something went wrong")
            return False

def deleteAuction(auctionId):
    with db:
        try:
            auction = Auction.get(Auction.auctionId == auctionId)
            auction.delete_instance()
            auction.save()
        except Exception:
            print(Exception)

def changeAuctionPrice(_price, auctionId):
    try:
        auction = Auction.get(Auction.auctionId == auctionId)
        if auction.price < _price:
            auction.price = _price
            auction.save()
            print("Ok")
            return True
        else:
            return False
    except DoesNotExist:
        print("Something went wrong!")
        return False            

def checkAuctionWinner(auctionId):
    try:
        auction = Auction.get(Auction.auctionId == auctionId)
        if auction.winner == "None":
            return 0
        elif auction.winner == "$begin$":
            return 1
        else:
            return -1
    except DoesNotExist:
        print("Something went wrong!")
        return False

def auctionBegin(auctionId):
    try:
        auction = Auction.get(Auction.auctionId == auctionId)
        auction.winner = "$begin$"
        auction.save()
    except Exception:
        print(Exception)

def isUserAuction(tgId):
    with db:
        try:
            user = UserTg.get(UserTg.tgId == tgId)
            if user.lastAuction == True:
                return True
            else:
                return False
        except DoesNotExist:
            print("Something went wrong")
            return False        

def getAllAuctionUser():
    with db:
        dict=[]
        for user in UserTg.select():
            if user.lastAuction == True:
                dict.append(user)
            else:
                pass
    # print('DONE Selecting')
    return dict

def resetAuction(_winner,auctionId):
    with db:
        try:
            auction = Auction.get(Auction.auctionId == auctionId)
            auction.winner = _winner
            auction.save()
            print("Setting auction winner is OK!")
            return True
        except Exception:
            print(Exception)
            return False

def insertRate(company, bet, auctionId):
    with db:
        temp = Rate(
               auctionId=auctionId,
               date=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
               company=company,
               bet=bet)
        try:
            temp.save()
            print('DONE inserting Bet')
        except:
            print("Something went wrong!")

def sortByTimeRate(auctionId):
    with db:
        try:
            dict = []
            for t in Rate.select()\
                    .where(Rate.auctionId == auctionId)\
                    .order_by(-Rate.date):
                dict.append(t)
            print('DONE sorting Rate')
            return dict
        except:
            print("Something went wrong!")
