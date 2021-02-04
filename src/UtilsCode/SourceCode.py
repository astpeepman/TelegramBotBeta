import emoji
import datetime
from dateutil import parser
from enum import IntEnum
from src.Modules.ProductModule import *
from src.UtilsCode.SqlCode import *
import telebot
from telebot import types
import codecs
from threading import Thread
import os
from copy import copy, deepcopy

bot = telebot.TeleBot('1591054566:AAGoTiGl3uty6kWMym40u5aB7Aygn95bLRU')

#INFO
INFORMATHIONS={}
def GetInfoFromDB():
    Infos=SelectInTable('Info', '*')
    for i in Infos:
        INFORMATHIONS[i[0]]=Info(i[0],i[3],i[1],i[2])




# СМАЙЛИКИ
EMOJI = [emoji.emojize(':pill:'), emoji.emojize(':mushroom:'), emoji.emojize('🍽')]
EMOJINUM=[emoji.emojize('0️⃣'),emoji.emojize('1️⃣'), emoji.emojize('2️⃣'),
          emoji.emojize('3️⃣'), emoji.emojize('4️⃣'), emoji.emojize('5️⃣'),
          emoji.emojize('6️⃣'), emoji.emojize('7️⃣'), emoji.emojize('8️⃣'), emoji.emojize('9️⃣')]

def NumToEmoji(num):
    x=''
    for i in str(num):
        x+=EMOJINUM[int(i)]
    return x

#Адрес самовывоза
MYADRESS='Воронежская 8к2'

#АдминАйдис
EgorId='717616464'
IlvirId='375747622'
TestAdminID='1223783387'

#Времена
TIMES=[]
TIMES.append('12:00')
TIMES.append('15:00')
TIMES.append('18:00')
TIMES.append('21:00')


#ТУт ПОНЯТНО
Clients=[]
Admins=[]
MainProducts=[]
Statuses=[]

#Обновление списка продуктов
def UpdateProducts():
    MainProducts.clear()
    ProductsBuff=SelectInTable('products')
    for i in ProductsBuff:
        ProductKinds=SelectInTable('kinds', '*', 'productId', int(i[0]))
        P=MainProduct()
        P.SetFromDB(i, ProductKinds)
        MainProducts.append(P)
        del P

#Получение продукта по АЙДИ
def GetProductById(id):
    for i in MainProducts:
        if i.ProductId==int(id):
            return i
    return None

#Перевод из строки в ДАТУ
def StringToDateTime(separately, StrDate, StrTime, StrDateTime=''):
    if separately==True:
        dateBuffer=StrDate.split('-')
        date=datetime.date(int(dateBuffer[0]), int(dateBuffer[1]), int(dateBuffer[2]))
        timeBuffer=StrTime.split(':')
        time=datetime.time(int(timeBuffer[0]), int(timeBuffer[1]), int(timeBuffer[2]))
        return date, time
    else:
        return parser.parse(StrDateTime)

#Проверка числа
def IntTypeCheck(mess):
    try:
        i = int(mess)
        if (i > 0):
            return i
        else:
            return -1
    except:
        return -2


def StringToTime(t):
    if t[0]=='0':
        hour=int(t[1])
    else: hour=int(str(t[0]+t[1]))
    if t[3]=='0':
        min=int(t[4])
    else: min=int(str(t[3]+t[4]))

    return datetime.time(hour, min)


def SendProductPresent(Product):
    text='ВНИМАНИЕ!!!\n' \
         'В наличие снова появился товар '+str(Product.Name)
    text+='\nПриятного аппетита)))'

class ImgTypes(IntEnum):
    ClientCheck=0
    AdminAddInfo=1

def CheckNumbersInString(s, count):
    i=0
    for k in str(s):
        try:
            x=int(k)
            i += 1

        except:
            print('cant NumberToStr')
            return -1
    if i != count:
        return -2

    return 1
