

from time import sleep
from src.UtilsCode.SourceCode import *
from src.Users.Client import *
from src.Users.Admin import *


import threading
mutex = threading.Lock()

Threads=[]


#АДМИНЫ
TestAdmin=Admin(bot, TestAdminID, 'TESTADMIN')
Admins.append(TestAdmin)

EgorAdmin=Admin(bot, EgorId, 'Егор')
Admins.append(EgorAdmin)

def NewClientToTable(message):
    client=SelectInTable('AllClients', '*', 'ClientId', str(message.chat.id))
    if client == []:
        addClient=f'''INSERT INTO
                        AllClients(`ClientId`, `ClientLogin`) 
                    VALUES
                        ('{str(message.chat.id)}', '{str(message.chat.username)}')'''
        execute_query(addClient)

def TimeOut():
    while True:
        for i in Clients:
            period = abs(i.LastActiveTime - datetime.datetime.now())
            if period.total_seconds()>3600:
                i.__del__()
                Clients.remove(i)
                print('Клиент ' + str(i.ClientId) + ' отключился')
        sleep(1)

def getAdmin(id):
    for a in Admins:
        if str(a.Id)==str(id):
            return a
    return None

def getRealClinet(id):
    for c in Clients:
        if c.ClientId==str(id):
            return c
    return None

def getClient(id):
    c=getRealClinet(id)
    if c is None:
        c=Client(bot, str(id), datetime.datetime.now())
        Clients.append(c)
        print('Клиент '+str(c.ClientId)+' присоединился')
    return c

def NotAdmin(id):
    for a in Admins:
        if str(id)==a.Id:
            return False
    return True

# @bot.message_handler(content_types=['photo'])
# def GetImg(message):
#     if NotAdmin(message.from_user.id):
#         mutex.acquire()
#         th2 = Thread(target=NewClientToTable, args=(message,))
#         th2.start()
#         c = getClient(message.from_user.id)
#         c.LastActiveTime = datetime.datetime.now()
#         c.GetImg(message)
#         mutex.release()
#


def GetCommands(message):
    if NotAdmin(message.from_user.id):
        th2 = Thread(target=NewClientToTable, args=(message,))
        th2.start()

        c = getClient(str(message.from_user.id))
        c.LastActiveTime = datetime.datetime.now()

        c.StartMessage()



def GetKey(call):
    if NotAdmin(call.message.chat.id):
        th2 = Thread(target=NewClientToTable, args=(call.message,))
        th2.start()

        c = getClient(call.message.chat.id)
        c.LastActiveTime = datetime.datetime.now()
        c.ClientCall(call)

    else:

        a=getAdmin(call.message.chat.id)
        a.KeyCommands(call)




def GetMessage(message):
    if NotAdmin(message.from_user.id)==False:

        a=getAdmin(message.from_user.id)
        a.TextCommands(message)

    else:
        #КЛИЕНТ ДЕЙСТВИЯ
        th2=Thread(target=NewClientToTable, args=(message,))
        th2.start()

        c=getClient(str(message.from_user.id))
        c.LastActiveTime=datetime.datetime.now()
        c.ClientMessage(message)


#ПРИНИМАЕМ ТЕКСТ
@bot.message_handler(content_types=['text'])
def MESSAGE(message):
    Thread(target=GetMessage, args=(message,)).start()

#ПРИНИМАЕМ КОМАНДУ
@bot.callback_query_handler(func=lambda call: True)
def CALL(call):
    Thread(target=GetKey, args=(call,)).start()

@bot.message_handler(commands=['start'])
def COMMANDS(message):
    Thread(target=GetCommands, args=(message,))



UpdateProducts()
GetInfoFromDB()

th = Thread(target=TimeOut, daemon=True)
th.start()
bot.polling(none_stop=True, interval=0)