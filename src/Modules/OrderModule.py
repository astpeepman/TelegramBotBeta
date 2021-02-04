from src.UtilsCode.SourceCode import *
from src.Modules.BasketModule import *
import emoji

class OrderStatusClass():
    def __init__(self, si=-1, text='', type=-1):
        self.StatusNum=si
        self.Text=text
        self.Type=type



class OrderStatus(IntEnum):
    S_AWAITINGPAY=0
    S_COMPLETED=1
    S_AWAITINGSEND=2
    S_SENT=3
    S_CANCELEDFROMSHOP=4
    S_AWAITINGCONFIRM=5
    S_AWAITMEETING=6
    S_CANCELEDFROMUSER = 7

# Получение Стринга Статуса
def GetStringOfOrderStatus(s):
    text=''
    if s == 0:
        text = 'Ожидает оплаты'
    elif s == 1:
        text = 'Завершен'
    elif s == 2:
        text = 'Подтвержден, ожидает отправки'
    elif s == 3:
        text = 'Отправлен (в пути)'
    elif s == 4:
        text = 'Отменен магазином'
    elif s == 5:
        text = 'Ожидает подтверждения магазином'
    elif s == 6:
        text = 'Подтвержден, ожидает встречи'
    elif s == 7:
        text = 'Отменен клиентом'
    return text

class OrderType(IntEnum):
    T_DELIBERY=0
    T_PICKUP=1



def GetStringOfOrderType(t):
    if t==0:
        text='Доставка'
    elif t==1:
        text='Самовывоз'
    return text


class Order():
    def __init__(self, B=Basket(), uid='', oid=-1):
        self.orderId = oid
        self.UserId = str(uid)
        self.UserName = ''
        self.Status = -1
        self.Type = -1
        self.Adress = ''
        self.MeetingDate = datetime.date(2021,1,1)
        self.MeetingTime = datetime.time(0,0,0)
        self.CreatingDateTime = datetime.datetime(2021,1,1,0,0,0)
        self.Basket=B.GetBasketFromDB()
        self.TrackNumber='0'
        self.UserLogin=''

    def NewOrder(self):
        addquery=f"""INSERT INTO
                        Orders(`userId`, `userName`, `type`, `adress`, `status`, `meetingDate`, `meetingTime`, `CREATINGDateTime`, `UserLogin`) 
                    VALUES
                        ('{self.UserId}', '{self.UserName}', {self.Type}, '{self.Adress}', {self.Status}, '{self.MeetingDate}', '{self.MeetingTime}','{self.CREATINGDateTime}', '{self.UserLogin}')
                    """
        self.orderId=execute_query(addquery)

        self.Basket.SaveToFormedDB(self.orderId)

    def UpdateOrderSatus(self):
        try:
            updatequery = f"""
                                                    UPDATE
                                                        Orders 
                                                    SET
                                                        `status`={self.Status}
                                                    WHERE `orderID`={self.orderId}
                                                    """
            execute_query(updatequery)

            return True
        except Exception as e:
            print(e)
            return False

    def GetorderFromDB(self):
        order = SelectInTable('Orders', '*', 'orderID', self.orderId)
        if order:
            date, time = StringToDateTime(True, order[0][6], order[0][8])
            self.MeetingDate = date
            self.MeetingTime = time
            self.UserId = order[0][1]
            self.UserName = order[0][2]
            self.Status = order[0][5]
            self.Type = order[0][3]
            self.Adress = order[0][4]
            self.CREATINGDateTime = StringToDateTime(False, '', '', order[0][7])
            #self.Basket.GetFromFormedDB(self.orderId)
            self.TrackNumber=order[0][9]
            self.UserLogin=str(order[0][10])

            return True
        else:
            return False

    def GetOrderString(self):
        basketBuff=deepcopy(self.Basket)
        if self.orderId==-1:
            text='ВАШ ЗАКАЗ:'
        else:
            if self.GetorderFromDB():
                text=f'ЗАКАЗ № {self.orderId}:'
                basketBuff.GetFromFormedDB(self.orderId)
            else:
                return None
        text+=basketBuff.GetStringBasket()
        text+='\n\n'+emoji.emojize('🙋')+'Получатель: '+str(self.UserName)+'\n'
        if self.Type == OrderType.T_PICKUP:
            text += emoji.emojize('🏪')+'Место получения: ' + str(self.Adress) + '\n'
            text += emoji.emojize('🕙')+'Дата  и время самовывоза: ' + str(self.MeetingDate.strftime("%d/%m/%Y")) + '' \
                                                                                                       ' ' + str(
                self.MeetingTime.strftime("%H:%M")) + '\n'
            text += '\n' + emoji.emojize('✅') + 'Сумма покупки составляет: ' + str(basketBuff.TotalPrice)
        else:
            text +=emoji.emojize('🏠')+'Адрес доставки: ' + str(self.Adress.split('+')[0]) + '\n'
            text+=emoji.emojize('#️⃣')+'Индекс: '+str(self.Adress.split('+')[1]) + '\n'
            if self.TrackNumber!='0':
                text+=f'Трек номер для отслеживания заказа: {self.TrackNumber}\n'
            text += '\n' + emoji.emojize('✅') + 'Сумма покупки составляет (с учетом доставки): ' + str(basketBuff.TotalPrice+350)



        if self.orderId != -1:
            text+=f'\n\n'+emoji.emojize('💼')+f'Статус заказа: {GetStringOfOrderStatus(self.Status)}'
        return text

    def OrderClear(self):
        self.__init__(uid=self.UserId)

    def SendOrderToAdmin(self, beginText='', fun=None):
        text=beginText
        text += self.GetOrderString()

        text+=f'\n\nЛогин клиента: @{self.UserLogin}'
        keyboard = types.InlineKeyboardMarkup()
        ConfirmKey = types.InlineKeyboardButton(text='Подтвердить',
                                                callback_data=f'ADMIN_ORDER_CONFIRM+' + str(self.orderId))
        CancelKey = types.InlineKeyboardButton(text='Отклонить',
                                               callback_data=f'ADMIN_ORDER_CANCEL+' + str(self.orderId))

        if self.Status==OrderStatus.S_AWAITINGCONFIRM:
            keyboard.add(ConfirmKey)
            keyboard.add(CancelKey)
        elif self.Type==OrderStatus.S_AWAITINGPAY:
            text+='\n!!!ЖДЕМ ЧЕК!!!'

        fun
        for a in Admins:
            bot.send_message(a.Id, text, reply_markup=keyboard)





#Статусы:
S_AWAITINGPAY=OrderStatusClass(0, 'Ожидает оплаты', OrderType.T_DELIBERY)
S_COMPLETED=OrderStatusClass(1, 'Завершен', -1)
S_AWAITINGSEND=OrderStatusClass(2, 'Ожидает отправки', OrderType.T_DELIBERY)
S_SENT=OrderStatusClass(3, 'Отправлен (В пути)', OrderType.T_DELIBERY)
S_CANCELEDFROMSHOP=OrderStatusClass(4, 'Отменен магазином', -1)
S_AWAITINGCONFIRM=OrderStatusClass(5, 'Ожидает подтверждения магазином', -1)
S_AWAITMEETING=OrderStatusClass(6, 'Ожидает встречи', OrderType.T_PICKUP)
S_CANCELEDFROMUSER = OrderStatusClass(6, 'Отменен клиентом', -1)


Statuses.append(S_AWAITINGPAY)
Statuses.append(S_COMPLETED)
Statuses.append(S_SENT)
Statuses.append(S_CANCELEDFROMSHOP)
Statuses.append(S_AWAITINGCONFIRM)
Statuses.append(S_AWAITMEETING)
Statuses.append(S_CANCELEDFROMUSER)

def GetStatus(id):
    for s in Statuses:
        if s.StatusNum==id:
            return s
    return None