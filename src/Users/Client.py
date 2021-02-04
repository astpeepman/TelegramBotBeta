from telebot import types
from src.UtilsCode.telegramcalendar import *
from src.Modules.OrderModule import *
from src.UtilsCode.SourceCode import MainProducts
import emoji



class Client():
    def __init__(self, bot, id='', t=datetime.datetime(2021,1,1,0,0)):
        self.ClientId=id
        self.Basket=Basket(self.ClientId).GetBasketFromDB()
        self.Order=Order(B=self.Basket, uid=self.ClientId)
        self.LastActiveTime=t
        self.BOT=bot

    def __del__(self):
        self.Basket.DeleteFromBasket()
        self.Order.OrderClear()

    def StartMessage(self):
        text = 'Приветствую тебя в нашем телеграм боте'
        text += '\nВот команды, которые я умею выполнять:'
        text += '\n/start - Начальное меню'
        text += '\n/products - Информация о товарах'
        # text+='\n/order - Сделать заказ'
        text += '\n/status - Узнать статус заказа'
        text += '\n/info - Информация и рекомендации'
        text += '\n/basket - Корзина'
        text += '\nВведите нужную вам команду или воспользуйтесь клавиатурой снизу'

        keyboard1 = types.ReplyKeyboardMarkup(True)

        StartKey = types.KeyboardButton(text='Начать')
        ProductsKey = types.KeyboardButton(text='Товары')
        StatusKey = types.KeyboardButton(text='Статус')
        InfoKey = types.KeyboardButton(text='Информация')
        BasketKey = types.KeyboardButton(text='Корзина ' + emoji.emojize('🧺'))

        keyboard1.add(StartKey, ProductsKey)
        keyboard1.add(StatusKey, InfoKey, BasketKey)

        text += '\n\nЕсли у вас вознили вопросы, можете написать нам: @Egor_mh'

        self.BOT.send_message(self.ClientId, text, reply_markup=keyboard1)

    def ShowAllProducts(self):
        keyboard = types.InlineKeyboardMarkup()
        for p in MainProducts:
            KeyBuff=types.InlineKeyboardButton(text=p.Name, callback_data='CLIENT_PRODUCTS_SHOW+'+str(p.ProductId))
            keyboard.add(KeyBuff)
        self.BOT.send_message(self.ClientId, text='Выберите товар из списка', reply_markup=keyboard)


    def ShowOneProduct(self, id):
        P=GetProductById(int(id))
        if P:
            text = P.GetProductString()
            keyboard = types.InlineKeyboardMarkup()
            KeyAddToBasket = types.InlineKeyboardButton(text='Добавить в корзину',
                                                        callback_data='CLIENT_BASKET_ADDTOBASKET+' + str(P.ProductId))
            KeyMainMenu = types.InlineKeyboardButton(text='Вернуться в меню', callback_data='CLIENT_TOMAIN')
            keyboard.add(KeyAddToBasket)
            keyboard.add(KeyMainMenu)
            self.BOT.send_photo(self.ClientId, open(str(P.Photo), 'rb'), caption=text, reply_markup=keyboard)
        else:
            pass

    def ShowBasket(self):
        keyboard = types.InlineKeyboardMarkup()
        if self.Basket.Products==[]:
            text='Ваша корзина пуста '+emoji.emojize('🤷')
        else:
            text = 'Ваша корзина ' +emoji.emojize('🧺')
            text+=self.Basket.GetStringBasket()

            KeyDeleteBasket = types.InlineKeyboardButton(text='Очистить корзину ' + emoji.emojize('🗑'),
                                                         callback_data='CLIENT_BASKET_CLEAN')
            KeyBuy = types.InlineKeyboardButton(text='Оформить заказ ' + emoji.emojize('💸'),
                                                callback_data='CLIENT_BASKET_BUY')
            keyboard.add(KeyDeleteBasket, KeyBuy)
            text += '\n\n'+emoji.emojize('✅')+'Сумма покупки составляет: ' + str(self.Basket.TotalPrice)
        self.BOT.send_message(self.ClientId, text, reply_markup=keyboard)

    def SendInfo(self, inf):
        fileObj = codecs.open(inf.TextFile, "r", "utf_8_sig" )
        text = fileObj.read()
        self.BOT.send_photo(self.ClientId, open(str(inf.ImgFile), 'rb'))
        self.BOT.send_message(self.ClientId, text)



    def AddProdToBasket(self, message, product):
        i = IntTypeCheck(message.text)
        if i == -1 or i == -2:
            self.BOT.send_message(self.ClientId, 'Ой, что-то пошло не так')
            self.ShowOneProduct(int(product.ProductId))
        else:
            self.Basket.AddToBasket(product, i)
            self.ShowBasket()

    def CheckOut(self, message, questNum):
        self.Order.Basket=self.Basket
        if questNum==1:
            self.Order.UserName=message.text

            try:
                self.Order.UserLogin = str(message.from_user.username)
            except:
                self.Order.UserLogin = 'НЕИЗВЕСТЕН'

            PayKeyboard = types.InlineKeyboardMarkup()
            Pickupkey = types.InlineKeyboardButton(text='Самовывоз', callback_data='СLIENT_ORDER_TYPE_PICKUP')
            DeliveryKEY = types.InlineKeyboardButton(text='Доставка', callback_data='СLIENT_ORDER_TYPE_DELIVERY')
            PayKeyboard.add(Pickupkey)
            PayKeyboard.add(DeliveryKEY)
            text = 'Выберите способ получения:\n1. Самовывоз. Оплата производится наличными или переводом' \
                   '\n2. Доставка. 100% предоплата переводом\nПочта России 1 класс (+350 рублей)'
            self.BOT.send_message(message.chat.id, text, reply_markup=PayKeyboard)
        elif questNum==3:
            self.BOT.send_message(message.chat.id, 'Выберите дату', reply_markup=create_calendar())
        elif questNum==4:
            TimeKeyboard = types.InlineKeyboardMarkup()
            for t in TIMES:
                keyBuff=types.InlineKeyboardButton(text=str(t), callback_data='СLIENT_ORDER_TIME+'+str(t))
                TimeKeyboard.add(keyBuff)

            self.BOT.send_message(message.chat.id, 'Выберите подходящее время', reply_markup=TimeKeyboard)
        elif questNum==5:
            text=self.Order.GetOrderString()
            COMFIRMKEY = types.InlineKeyboardButton(text='ПОДТВЕРДИТЬ', callback_data='СLIENT_ORDER_CONFIRM')
            CANCELKEY = types.InlineKeyboardButton(text='ОТМЕНИТЬ', callback_data='СLIENT_ORDER_CANCEL')
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(COMFIRMKEY)
            keyboard.add(CANCELKEY)

            self.BOT.send_message(message.chat.id, text, reply_markup=keyboard)



    def GetDeliveryAdress(self, message, step):
        if step==1:
            self.Order.Adress=message.text
            self.BOT.send_message(self.ClientId, 'Введите, пожалуйста, индекс')
            self.BOT.register_next_step_handler(message, self.GetDeliveryAdress, 2)
        if step==2:
            if CheckNumbersInString(message.text, 6)==1:
                self.Order.Adress+='+'+str(message.text)
                self.BOT.send_message(self.ClientId,
                                      'После оформления заказа, вам необходимо будет подтвердить оплату, прислав электронный чек (скриншот)'
                                      '\nВ случае отсутствия электроннного чека, в течение 2-х дней, заказ будет отменён')
                self.CheckOut(message, 5)
            else:
                keyboard=types.InlineKeyboardMarkup()
                KeyMainMenu = types.InlineKeyboardButton(text='Вернуться в меню', callback_data='CLIENT_TOMAIN')
                KeyAgain=types.InlineKeyboardButton(text='Ввести индекс еще раз', callback_data='СLIENT_ORDER_INDEX_AGAIN')
                keyboard.add(KeyAgain)
                keyboard.add(KeyMainMenu)
                self.BOT.send_message(self.ClientId, 'Что-то пошло не так, попробуйте ввести индекс еще раз', reply_markup=keyboard)



    def GetPickupDate(self, call):
        selected, date = process_calendar_selection(self.BOT, call)
        if selected:
            self.BOT.send_message(chat_id=call.from_user.id,
                                  text="Дата встречи: %s" % (date.strftime("%d/%m/%Y")))
            self.Order.MeetingDate = date
            self.CheckOut(call.message, 4)

    def GetPickupTime(self, call):

        time = call.data.split('+')[1]



        self.Order.MeetingTime = StringToTime(time)
        text = "Время встречи: %s" % (self.Order.MeetingTime.strftime("%H:%M"))
        self.BOT.edit_message_text(text=text,
                                   chat_id=call.message.chat.id,
                                   message_id=call.message.message_id
                                   )
        self.CheckOut(call.message, 5)


    def OrderConfirm(self, call):
        self.Order.CREATINGDateTime=datetime.datetime.now()
        self.Order.NewOrder()
        text = f'Ваш заказ успешно оформлен. Номер вашего заказа: {self.Order.orderId}\n\n'
        if self.Order.Type == OrderType.T_PICKUP:
            text += 'Ожидайте подтверждения заказа!\n'
        elif self.Order.Type==OrderType.T_DELIBERY:
            text += f'Вам нужно отправить {self.Basket.TotalPrice+350} РУБЛЕЙ на КАРТУ 0000 0000 0000 0000 и прислать скриншот чека в течение 2-х дней для подтверждения заказа. ' \
                    f'\n*Сделать это можно следующим образом:*' \
                    f'\n*1) Команда /status (или кнопка "Статус" на клавиатуре).*' \
                    f'\n*2) Находите свой заказ по номеру.*' \
                    f'\n*3) Нажимаете кнопку "Подтвердить оплату".*'
        text += '\n\nЕсли у нас возникнут вопросы по вашему заказу, мы свяжемся с вами!'

        self.Order.SendOrderToAdmin('Поступил новый заказ\n')
        self.Basket.DeleteFromBasket()

        self.BOT.edit_message_text(text=call.message.text,
                                   chat_id=call.message.chat.id,
                                   message_id=call.message.message_id
                                   )
        bot.send_message(self.ClientId, text=text, parse_mode="Markdown")
        self.BOT.answer_callback_query(call.id, show_alert=True, text=f"ЗАКАЗ ОФОРМЛЕН. НОМЕР ВАШЕГО ЗАКАЗА: {self.Order.orderId}")

        self.Order.OrderClear()


    def FormedOrderCancel(self, call):
        self.Order.orderId=int(call.data.split('+')[1])
        self.Order.GetorderFromDB()
        if self.Order.Status==OrderStatus.S_AWAITINGPAY or self.Order.Status==OrderStatus.S_AWAITINGCONFIRM or self.Order.Status==OrderStatus.S_AWAITMEETING:
            self.Order.Status=OrderStatus.S_CANCELEDFROMUSER
            if self.Order.UpdateOrderSatus():
                text='Вы отменили покупку'
                self.BOT.answer_callback_query(call.id, show_alert=True,
                                               text=text)
                self.Order.SendOrderToAdmin(beginText='!!!КЛИЕНТ ОТМЕНИЛ ЗАКАЗ!!!\n')
                self.Order.OrderClear()
            else:
                text='Что-то пошло не так. Попробуйте еще раз' \
                     'В случае, если ошибка возникнет еще раз, обратитесь сюда: @Skulap1'
            self.BOT.edit_message_text(text=text,
                                       chat_id=call.message.chat.id,
                                       message_id=call.message.message_id
                                       )
        else:
            text='Вы не можете отменить данный заказ!'
            self.BOT.answer_callback_query(call.id, show_alert=True,
                                           text=text)


    def GetImg(self, message, photoType):
        if message.photo is not None:
            if photoType==ImgTypes.ClientCheck:
                self.Order.Status = OrderStatus.S_AWAITINGCONFIRM
                self.Order.UpdateOrderSatus()

                file_info = self.BOT.get_file(message.photo[len(message.photo) - 1].file_id)
                downloaded_file = self.BOT.download_file(file_info.file_path)
                src = f'src/ClientChecks/Order_{self.Order.orderId}.jpg'
                with open(src, 'wb') as new_file:
                    new_file.write(downloaded_file)

                text = f'!!!ПО ЗАКАЗУ №{self.Order.orderId} клиент прислал фото чека!!!\n\n'
                def Yo():
                    for i in Admins:
                        self.BOT.send_photo(i.Id, downloaded_file, caption=f'Чек по заказу №{self.Order.orderId}')

                self.Order.SendOrderToAdmin(beginText=text, fun=Yo())

                self.Order.OrderClear()
                text='Фото добавлено.\n' \
                     'После проверки администратор подтвердит ваш заказ и отправит в течение текущего  дня,' \
                     ' если заказ сделан до 17:30 по мск.'
                self.BOT.reply_to(message, text)
            else:
                self.BOT.send_message(self.ClientId, 'Не понимаю к чему эта фотография, но спасибо)')
        else:
            bot.send_message(self.ClientId, 'Ожидалась фотография, но ее нет 🙁')
            self.StartMessage()




    def Orderfunction(self, call):
        if call.data.startswith('СLIENT_ORDER_TYPE'):
            self.BOT.edit_message_text(text=call.message.text,
                                       chat_id=call.message.chat.id,
                                       message_id=call.message.message_id
                                       )
            if call.data=='СLIENT_ORDER_TYPE_PICKUP':
                self.Order.Type=OrderType.T_PICKUP
                self.Order.Adress=MYADRESS
                self.Order.Status=OrderStatus.S_AWAITINGCONFIRM
                self.BOT.answer_callback_query(call.id, show_alert=True, text='Адрес самовывоза: Москва, '
                                                                              'ул. Воронежская 8к2 (м. Домодедовская)')
                self.BOT.send_message(call.message.chat.id, 'Адрес самовывоза: Москва, '
                                                            'ул. Воронежская 8к2 (м. Домодедовская)\n')
                self.CheckOut(call.message, 3)
            elif call.data=='СLIENT_ORDER_TYPE_DELIVERY':
                self.Order.Type=OrderType.T_DELIBERY
                self.Order.Status=OrderStatus.S_AWAITINGPAY
                self.BOT.send_message(self.ClientId, 'Напишите адрес доставки')
                self.BOT.register_next_step_handler(call.message, self.GetDeliveryAdress, 1)
        elif call.data.startswith('СLIENT_ORDER_DATE'):
            self.GetPickupDate(call)
        elif call.data.startswith('СLIENT_ORDER_TIME'):
            self.GetPickupTime(call)

        elif call.data=='СLIENT_ORDER_CONFIRM':
            self.OrderConfirm(call)
        elif call.data=='СLIENT_ORDER_CANCEL':
            self.BOT.answer_callback_query(call.id, show_alert=True,
                                           text='Вы отменили покупку')
            self.BOT.edit_message_text(text='Вы отменили покупку',
                                       chat_id=call.message.chat.id,
                                       message_id=call.message.message_id
                                       )
            self.Order.OrderClear()
            self.StartMessage()
        elif call.data.startswith('СLIENT_ORDER_FORMED_CANCEL'):
            self.FormedOrderCancel(call)
        elif call.data.startswith('СLIENT_ORDER_FORMED_PAY_CONFIRM'):
            self.BOT.edit_message_text(text=call.message.text,
                                    chat_id=call.message.chat.id,
                                    message_id=call.message.message_id)
            self.BOT.send_message(self.ClientId, text='Пришлите скрин/фотографию чека')
            self.Order=Order(oid=int(call.data.split('+')[1]))
            bot.register_next_step_handler(call.message, self.GetImg, ImgTypes.ClientCheck)
        elif call.data=='СLIENT_ORDER_INDEX_AGAIN':
            self.BOT.edit_message_text(text='Введите, пожалуйста, индекс',
                                       chat_id=call.message.chat.id,
                                       message_id=call.message.message_id)
            self.BOT.register_next_step_handler(call.message, self.GetDeliveryAdress, 2)



    def BasketFunction(self, call):
        if call.data.startswith('CLIENT_BASKET_ADDTOBASKET'):
            P = GetProductById(int(call.data.split('+')[1]))
            if P.Present==True:
                if len(P.Kinds)==1:
                    P2 = ClientProduct(kindId=int(P.Kinds[0]))
                    self.BOT.send_message(self.ClientId, 'Введите количество')
                    self.BOT.register_next_step_handler(call.message, self.AddProdToBasket, P2)
                else:
                    keyboard=types.InlineKeyboardMarkup()
                    i=0
                    for k in P.Kinds:
                        KeyBuff=InlineKeyboardButton(text=GetKindById(k)[0][2]+' - '+str(P.Prices[i])+'₽', callback_data='CLIENT_PRODUCTS_CATEGORY+'+str(k))
                        i+=1
                        keyboard.add(KeyBuff)
                    self.BOT.send_message(self.ClientId, text='Выберите категорию данного товара', reply_markup=keyboard)
            else:
                text='К сожалению данного товара сейчас нет в наличии. Как только он снова у нас появится, мы вам непременно сообщим об этом'
                self.BOT.send_message(self.ClientId, text=text)
        elif call.data=='CLIENT_BASKET_CLEAN':
            self.Basket.DeleteFromBasket()
            self.BOT.edit_message_text(text='Вы очистили корзину, теперь она пуста'+emoji.emojize('🙂'),
                                    chat_id=call.message.chat.id,
                                    message_id=call.message.message_id
                                    )

        elif call.data=='CLIENT_BASKET_BUY':
            self.BOT.edit_message_text(text=call.message.text,
                                    chat_id=call.message.chat.id,
                                    message_id=call.message.message_id
                                    )
            self.BOT.send_message(self.ClientId, 'Как вас зовут? (ФИО полностью)')
            self.BOT.answer_callback_query(call.id, show_alert=True, text="Обязательно вводите ФИО полностью. Это потребуется "
                                                      "для оформления доставки " +emoji.emojize('🏃‍♂️')+ " ,а так же для скидки постоянного клиента "+emoji.emojize('👍'))
            self.BOT.register_next_step_handler(call.message, self.CheckOut, 1)


    def FindOrder(self, message, step):
        if step == 1:
            self.BOT.send_message(self.ClientId, 'Введите номер заказа')
            self.BOT.register_next_step_handler(message, self.FindOrder, 2)
        elif step==2:
            i = IntTypeCheck(message.text)

            if i == -1 or i == -2:
                self.BOT.send_message(self.ClientId, 'Ой, что-то пошло не так')
                self.StartMessage()
            else:
                o=Order(oid=i)
                text=o.GetOrderString()
                if text:
                    if o.UserId==str(message.from_user.id):
                        keyboard = types.InlineKeyboardMarkup()
                        if o.Status==OrderStatus.S_AWAITINGPAY:
                            confKey = types.InlineKeyboardButton(text='Подтвердить оплату',
                                                                 callback_data='СLIENT_ORDER_FORMED_PAY_CONFIRM+' + str(
                                                                    o.orderId))
                            keyboard.add(confKey)
                        if o.Status==OrderStatus.S_AWAITINGPAY or o.Status==OrderStatus.S_AWAITINGCONFIRM or o.Status==OrderStatus.S_AWAITMEETING:
                            cancelKey=types.InlineKeyboardButton(text='Отменить заказ',
                                                                     callback_data='СLIENT_ORDER_FORMED_CANCEL+' + str(
                                                                        o.orderId))
                            keyboard.add(cancelKey)
                        self.BOT.send_message(self.ClientId, text, reply_markup=keyboard)
                    else:
                        self.BOT.send_message(self.ClientId, 'Нет соответствия номера заказа с вашим логином в базе')
                else:
                    self.BOT.send_message(self.ClientId, 'Такого заказа не существует')


    def ClientMessage(self, message):
        try:
            print(self.ClientId, 'Нажал на ', message.text)
            if message.text=='/start' or message.text=='Начать':
                self.StartMessage()
            if message.text=='/products' or message.text=='Товары':
                self.ShowAllProducts()
            if message.text=='/basket' or message.text=='Корзина ' + emoji.emojize('🧺'):
                self.ShowBasket()
            if message.text=='/status' or message.text=='Статус':
                self.FindOrder(message,1)
            if message.text=='/info' or message.text=='Информация':
                keyboard=types.InlineKeyboardMarkup()
                for value in INFORMATHIONS.values():
                    KeyBuf=types.InlineKeyboardButton(text=value.Name, callback_data='CLIENT_INFO+'+str(value.Id))
                    keyboard.add(KeyBuf)
                bot.send_message(self.ClientId,text='Выберите категорию', reply_markup=keyboard)
        except Exception as e:
            print('Ошибка::', e)


    def ClientCall(self, call):
        try:
            print(self.ClientId, 'Нажал на ', call.data)
            if call.data.startswith('CLIENT_PRODUCTS_SHOW'):
                self.ShowOneProduct(call.data.split('+')[1])
            elif call.data.startswith('CLIENT_BASKET'):
                self.BasketFunction(call)
            elif call.data.startswith('CLIENT_PRODUCTS_CATEGORY'):
                P2 = ClientProduct(kindId=int(call.data.split('+')[1]))
                text='Вы выбрали: "'+str(P2.Name)+' ('+str(P2.StringKind)+')"'
                text+='\n\nВведите количество товара для заказа'
                self.BOT.edit_message_text(text=text,
                                           chat_id=call.message.chat.id,
                                           message_id=call.message.message_id
                                           )
                self.BOT.register_next_step_handler(call.message, self.AddProdToBasket, P2)
            elif call.data.startswith('СLIENT_ORDER'):
                self.Orderfunction(call)
            elif call.data=='CLIENT_TOMAIN':
                self.StartMessage()

            elif call.data.startswith('CLIENT_INFO'):
                self.BOT.edit_message_text(text=call.message.text,
                                           chat_id=call.message.chat.id,
                                           message_id=call.message.message_id
                                           )
                self.SendInfo(INFORMATHIONS[int(call.data.split('+')[1])])
        except Exception as e:
            print('Ошибка::', e)

