from telebot import types
from src.UtilsCode.SourceCode import *
from src.Modules.OrderModule import *
import emoji
import xlwt, xlrd, xlutils

class Admin():
    def __init__(self, bot, ai='', an=''):
        self.Id=ai
        self.Name=an
        self.BOT=bot
        self.InfoBuff=Info()


    def StartMessage(self):
        text = 'Админ панель. Используйте команды:'
        text += '\n/start - начало работы'
        text += '\n/neworders - новые заказы'
        text += '\n/find - найти заказ'
        text += '\n/report - запросить отчет'
        text+='\n/products - посмотреть товары'
        text+='\n/info - информации'
        #text += '\n/product - наличие товара'

        StartKey = types.KeyboardButton(text='Старт')
        NewOrdersKey = types.KeyboardButton(text='Новые')
        FindKey = types.KeyboardButton(text='Поиск')
        ReportKey = types.KeyboardButton(text='Отчет')
        ProductsKey=types.KeyboardButton(text='Товары')
        InfoKey=types.KeyboardButton(text='Инфо')

        keyboard = types.ReplyKeyboardMarkup(True)

        keyboard.add(StartKey, NewOrdersKey,FindKey)
        keyboard.add(ReportKey, ProductsKey, InfoKey)

        self.BOT.send_message(self.Id, text=text, reply_markup=keyboard)

    def GetNewOrders(self):
        NotConfirmOrders = SelectInTable('Orders','*','status', 5)
        if len(NotConfirmOrders)==0:
            self.BOT.send_message(self.Id, 'Новых заказов пока нет')
        else:
            text = '!!!Вот все заказы, которые ждут подтверждения: \n\n'
            i=1
            for o in NotConfirmOrders:
                orderBuff=Order(oid=int(o[0]))
                orderBuff.GetorderFromDB()
                text=orderBuff.GetOrderString()
                keyboard = types.InlineKeyboardMarkup()
                ConfirmKey = types.InlineKeyboardButton(text='Подтвердить',
                                                        callback_data=f'ADMIN_ORDER_CONFIRM+' + str(o[0]))
                CancelKey = types.InlineKeyboardButton(text='Отклонить',
                                                       callback_data=f'ADMIN_ORDER_CANCEL+' + str(o[0]))
                if orderBuff.Type==OrderType.T_PICKUP:
                    keyboard.add(ConfirmKey)
                    keyboard.add(CancelKey)
                elif orderBuff.Type==OrderType.T_DELIBERY:
                    text+='\n!!!ЖДЕМ ЧЕК!!!'
                self.BOT.send_message(self.Id, text, reply_markup=keyboard)
                text = ''
                orderBuff.OrderClear()

    def SendStatusToClient(self, orderId):
        buff = SelectInTable('Orders', '*', 'orderID', orderId)
        if buff:
            text = f'Ваш заказ №{orderId} имеет статус "{GetStringOfOrderStatus(int(buff[0][5]))}"'
            if int(buff[0][5])!=OrderStatus.S_CANCELEDFROMSHOP and int(buff[0][5])!=OrderStatus.S_CANCELEDFROMUSER:
                if int(buff[0][3]) == OrderType.T_PICKUP:
                    text += '\nДля связи с продавцом звоните по тел.: +79166495131'
                elif buff[0][9]!='0':
                    text+=f'\nВаш трек-номер для отслеживания заказа: {buff[0][9]}'
            self.BOT.send_message(buff[0][1], text)

    def OrderConfirm(self, id, key):
        orderBuff=SelectInTable('Orders', '*', 'orderID', int(id))
        newStatus=-1
        text=''
        if orderBuff is None:
            text='Заказ не найден'
        elif int(orderBuff[0][5])!=5 and int(orderBuff[0][5])!=0:
            text=f'!Заказ уже имеет статус: "{GetStringOfOrderStatus(orderBuff[0][5])}"!'
        elif key==1:
            if orderBuff[0][3]==1:
                newStatus=6
            else:
                newStatus=2
            text='Заказ подтвержден!'
        elif key==2:
            if orderBuff[0][3] == 1:
                newStatus=4
                text='Заказ отменен!'
            else:
                newStatus=0
                text='Продолжаем ждать чек'
        if newStatus!=-1:
            changestatus = f"""
                                                UPDATE
                                                    Orders 
                                                SET
                                                    `status`={newStatus}
                                                WHERE `orderID`={id}
                                                """
            execute_query(changestatus)

            self.SendStatusToClient(id)
        return text


    def SendInfo(self, inf):
        fileObj = codecs.open(inf.TextFile, "r", "utf_8_sig" )
        text = fileObj.read()
        self.BOT.send_photo(self.Id, open(str(inf.ImgFile), 'rb'))

        keyboard=types.InlineKeyboardMarkup()
        DeleteKey=types.InlineKeyboardButton(text='Удалить', callback_data='ADMIN_DELETE_INFO+'+str(inf.Id))
        keyboard.add(DeleteKey)
        self.BOT.send_message(self.Id, text, reply_markup=keyboard)


    def GetImg(self, message, imgtype):
        if message.photo is not None:
            if imgtype==ImgTypes.AdminAddInfo:
                file_info = self.BOT.get_file(message.photo[len(message.photo) - 1].file_id)
                downloaded_file = self.BOT.download_file(file_info.file_path)
                src = f'src/ImgInfo/info_{len(INFORMATHIONS)+1}.jpg'
                with open(src, 'wb') as new_file:
                    new_file.write(downloaded_file)

                self.InfoBuff.ImgFile=f'src/ImgInfo/info_{len(INFORMATHIONS)+1}.jpg'
                bot.send_message(self.Id, 'Пришлите текст')
                bot.register_next_step_handler(message, self.AddNewInfo, 2)

    def AddNewInfo(self, message, step):
        if step==1:
            self.InfoBuff.Name=message.text
            bot.send_message(self.Id, 'Пришлите фотографию')
            bot.register_next_step_handler(message, self.GetImg, ImgTypes.AdminAddInfo)
        if step==2:
            text=message.text
            file=codecs.open(f'src/TextInfo/info_{str(len(INFORMATHIONS)+1)}.txt', mode='w', encoding = 'utf-8')
            file.write(text)
            file.close()
            self.InfoBuff.TextFile=f'src/TextInfo/info_{str(len(INFORMATHIONS)+1)}.txt'
            self.InfoBuff.SaveToDb()
            GetInfoFromDB()
            bot.send_message(self.Id, 'Готово')

    def FindOrder(self, message, step):
        if step==1:
            self.BOT.send_message(self.Id, 'Введите номер заказа')
            self.BOT.register_next_step_handler(message, self.FindOrder, 2)
        if step==2:
            i=IntTypeCheck(message.text)
            if i==-1 or i==-2:
                self.BOT.send_message(self.Id, 'Ой, что-то пошло не так')
                self.StartMessage()
            else:
                o = Order(oid=i)
                text = o.GetOrderString()
                if text:
                    text+=f'\n\nЛогин клиента: @{o.UserLogin}'
                    keyboard = types.InlineKeyboardMarkup()
                    ChangeStatusKey = types.InlineKeyboardButton(text='Изменить статус',
                                                                 callback_data='ADMIN_ORDER_CHANGESTATUS+' + str(i))
                    keyboard.add(ChangeStatusKey)
                    self.BOT.send_message(self.Id, text, reply_markup=keyboard)
                else:
                    self.BOT.send_message(self.Id, 'Такого заказа не существует')

    def AddTrackNumber(self, message, orderid):
            addquery=f'''
                                                    UPDATE
                                                            Orders 
                                                        SET
                                                            `trackNum`={str(message.text)}
                                                        WHERE `orderID`={int(orderid)}
            
            '''
            execute_query(addquery)
            bot.send_message(self.Id, 'Трек номер добавлен!')
            self.SendStatusToClient(int(orderid))


    def ChangeStatus(self, call):
        calldata=call.data.split('+')
        if len(calldata)==2:
            keyboard=types.InlineKeyboardMarkup()
            i=0
            while i < 8:
                Key1 = types.InlineKeyboardButton(text=GetStringOfOrderStatus(i),
                                                  callback_data='ADMIN_ORDER_CHANGESTATUS+' + str(calldata[1]) + '+' + str(i))
                i += 1
                keyboard.add(Key1)

            self.BOT.send_message(self.Id, text='Выберите новый статус', reply_markup=keyboard)

        if len(calldata)==3:
            changestatus = f"""
                                                        UPDATE
                                                            Orders 
                                                        SET
                                                            `status`={int(calldata[2])}
                                                        WHERE `orderID`={int(calldata[1])}
                                                        """
            execute_query(changestatus)
            self.BOT.send_message(self.Id, f'Заказ #{calldata[1]} имеет статус "{GetStringOfOrderStatus(int(calldata[2]))}"')


            if int(calldata[2]) == 3:
                text = 'Введите трек номер'
                bot.send_message(self.Id, text)
                bot.register_next_step_handler(call.message, self.AddTrackNumber, int(calldata[1]))
            else:
                self.SendStatusToClient(int(calldata[1]))


    def ShowAllProducts(self):
        keyboard = types.InlineKeyboardMarkup()
        for p in MainProducts:
            KeyBuff = types.InlineKeyboardButton(text=p.Name, callback_data='ADMIN_PRODUCTS_SHOW+' + str(p.ProductId))
            keyboard.add(KeyBuff)

        keyAdd=types.InlineKeyboardButton(text='ДОБАВИТЬ ТОВАР!', callback_data='ADMIN_PRODUCTS_ADDNEW')
        keyboard.add(keyAdd)
        self.BOT.send_message(self.Id, text='Выберите товар из списка', reply_markup=keyboard)

    def ShowOneProduct(self, id):
        P=GetProductById(int(id))
        if P:
            text = P.GetProductString()

            text+='\nВ наличии: '
            if P.Present:
                text+='ДА!'
            else:
                text+='НЕТ!'

            keyboard = types.InlineKeyboardMarkup()
            KeyAddToBasket = types.InlineKeyboardButton(text='Изменить наличие',
                                                        callback_data='ADMIN_PRODUCT_PRESENT+' + str(P.ProductId))
            keyboard.add(KeyAddToBasket)
            self.BOT.send_photo(self.Id, open(str(P.Photo), 'rb'), caption=text, reply_markup=keyboard)
        else:
            pass

    def ChangePresent(self, id):
        P = GetProductById(int(id))

        if P.Present:
            P.Present=False
        else:
            P.Present=True
            AllClientsIDs=SelectInTable('AllClients', 'ClientId')

            text1=emoji.emojize('🆘')+'Уважаемые подписчики, у нас снова появился в наличии следующий товар:'

            text = P.GetProductString()
            for c in AllClientsIDs:
                bot.send_message(c[0], text1)
                bot.send_photo(c[0], open(str(P.Photo), 'rb'), caption=text)

            bot.send_message('-1001403274709', text1)
            bot.send_photo('-1001403274709', open(str(P.Photo), 'rb'), caption=text)


        if P.UpdateProduct():
            text='Успешно'
            UpdateProducts()
        else:
            text='НЕУСПЕШНО БЕЛЯАТЬ'
        self.BOT.send_message(self.Id, text)
        return text


    def TextCommands(self, message):
        try:
            if message.text == '/start' or message.text == 'Старт':
                self.StartMessage()
            if message.text == '/neworders' or message.text == 'Новые':
                self.GetNewOrders()
            if message.text == '/find' or message.text == 'Поиск':
                self.FindOrder(message, 1)
            if message.text=='/products' or message.text=='Товары':
                self.ShowAllProducts()
            if message.text=='/info' or message.text=='Инфо':
                keyboard = types.InlineKeyboardMarkup()
                for value in INFORMATHIONS.values():
                    KeyBuf = types.InlineKeyboardButton(text=value.Name,
                                                        callback_data='ADMIN_INFO+' + str(value.Id))
                    keyboard.add(KeyBuf)
                NewKey=types.InlineKeyboardButton(text='Добавить', callback_data='ADMIN_NEW_INFO')
                keyboard.add(NewKey)
                bot.send_message(self.Id, text='Выберите категорию', reply_markup=keyboard)
            if message.text=='/report' or message.text=='Отчет':
                bot.send_message(self.Id, 'Я формирую отчет! Можете заниматься своими делами')
                th = Thread(target=self.ToExcel)
                th.start()

        except Error as e:
            print('Ошибка у админа', e)

    def KeyCommands(self, call):
        try:
            if call.data.startswith('ADMIN_ORDER_CHANGESTATUS'):
                self.BOT.edit_message_text(
                    text=call.message.text,
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id
                )
                self.ChangeStatus(call)

            elif call.data.startswith('ADMIN_ORDER_CONFIRM'):
                try:
                    self.BOT.edit_message_text(
                        text=call.message.text + '\n\n\n' + str(self.OrderConfirm(call.data.split('+')[1], 1)),
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id
                        )
                except:
                    pass
            elif call.data.startswith('ADMIN_ORDER_CANCEL'):
                try:
                    self.BOT.edit_message_text(text=call.message.text+'\n\n\n'+str(self.OrderConfirm(call.data.split('+')[1], 2)),
                                               chat_id=call.message.chat.id,
                                               message_id=call.message.message_id
                                               )
                except:
                    pass

            elif call.data.startswith('ADMIN_PRODUCTS_SHOW'):
                self.ShowOneProduct(call.data.split('+')[1])
            elif call.data.startswith('ADMIN_PRODUCT_PRESENT'):
                self.ChangePresent(call.data.split('+')[1])
            elif call.data.startswith('ADMIN_INFO'):
                self.BOT.edit_message_text(text=call.message.text,
                                           chat_id=call.message.chat.id,
                                           message_id=call.message.message_id
                                           )
                self.SendInfo(INFORMATHIONS[int(call.data.split('+')[1])])
            elif call.data=='ADMIN_NEW_INFO':
                text='Введите название'
                bot.send_message(self.Id, text)
                bot.register_next_step_handler(call.message, self.AddNewInfo, 1)

            elif call.data.startswith('ADMIN_DELETE_INFO'):
                try:
                    deletequery=f'''DELETE FROM INFO WHERE Id=={int(call.data.split('+')[1])}'''
                    execute_query(deletequery)

                    del INFORMATHIONS[int(call.data.split('+')[1])]
                    bot.edit_message_text(
                        text='Успешно удалено',
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id
                    )
                except Error as e:
                    text='Что то пошло не так'
                    text+='\n'+str(e)
                    bot.send_message(self.Id, text)
        except Error as e:
            print('Ошибка у админа', e)

    def ToExcel(self):
        wb = xlwt.Workbook()
        ws = wb.add_sheet('Отчет')
        Orders = SelectInTable('Orders', '*')

        ws.write(0, 0, 'Номер заказа')
        ws.write(0, 1, 'Аккаунт')
        ws.write(0, 2, 'ФИО')
        ws.write(0, 3, 'Тип заказа')
        ws.write(0, 4, 'Адрес')
        ws.write(0, 5, 'Статус')
        ws.write(0, 6, 'Дата встречи')
        ws.write(0, 7, 'Время встречи')
        ws.write(0, 8, 'Дата создания заказа')
        ws.write(0, 9, 'Продукт')
        ws.write(0, 10, 'Категория продукта')
        ws.write(0, 11, 'Количество')
        ws.write(0, 12, 'Цена')

        j = 1
        for order in Orders:
            ws.write(j, 0, order[0])
            login = SelectInTable('AllClients', 'ClientLogin', 'ClientId', order[1])
            try:
                ws.write(j, 1, login[0][0])
            except:
                ws.write(j,1, 'Неизвестно')
            ws.write(j, 2, order[2])

            orderType = GetStringOfOrderType(order[3])
            ws.write(j, 3, orderType)
            ws.write(j, 4, order[4])

            ws.write(j, 5, GetStringOfOrderStatus(order[5]))
            ws.write(j, 6, order[6])
            ws.write(j, 7, order[8])
            ws.write(j, 8, order[7])

            formedBasket = SelectInTable('formed_baskets', '*', 'orderId', order[0])
            products = SelectInTable('formed_baskets_products', '*', 'basketId', formedBasket[0][0])
            for p in products:
                kind = GetKindById(p[3])
                ws.write(j, 9, GetProductNameById(p[1]))
                ws.write(j, 10, kind[0][2])
                ws.write(j, 11, p[2])
                ws.write(j, 12, kind[0][3] * p[2])
                j += 1
            ws.write(j, 11, 'ИТОГО:')
            ws.write(j, 12, formedBasket[0][1])
            j += 1

        DocName='Order_report_' + str(datetime.datetime.now().strftime("%m-%d-%Y_%H-%M-%S")) + '.xls'
        wb.save(DocName)

        bot.send_document(self.Id, open(DocName, 'rb'))
        os.remove(DocName)


