import calendar
import datetime

from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


def create_callback_data(action,year,month,day):
    return ";".join([action,str(year),str(month),str(day)])

def separate_callback_data(data):
    return data.split(";")


def create_calendar(year=None,month=None):
    now = datetime.datetime.now()
    if year == None: year = now.year
    if month == None: month = now.month
    data_ignore = create_callback_data("СLIENT_ORDER_DATE_IGNORE", year, month, 0)
    keyboard = []
    #First row - Month and Year
    row=[]
    row.append(InlineKeyboardButton(calendar.month_name[month]+" "+str(year),callback_data=data_ignore))
    keyboard.append(row)
    #Second row - Week Days
    row=[]
    for day in ["ПН","ВТ","СР","ЧТ","ПТ","СБ","ВС"]:
        row.append(InlineKeyboardButton(day,callback_data=data_ignore))
    keyboard.append(row)

    my_calendar = calendar.monthcalendar(year, month)
    for week in my_calendar:
        row=[]
        for day in week:
            if(day==0):
                row.append(InlineKeyboardButton(" ",callback_data=data_ignore))
            else:
                row.append(InlineKeyboardButton(str(day),callback_data=create_callback_data("СLIENT_ORDER_DATE_DAY",year,month,day)))
        keyboard.append(row)
    #Last row - Buttons
    row=[]
    row.append(InlineKeyboardButton("<",callback_data=create_callback_data("СLIENT_ORDER_DATE_PREV-MONTH",year,month,day)))
    row.append(InlineKeyboardButton(" ",callback_data=data_ignore))
    row.append(InlineKeyboardButton(">",callback_data=create_callback_data("СLIENT_ORDER_DATE_NEXT-MONTH",year,month,day)))
    keyboard.append(row)

    return InlineKeyboardMarkup(keyboard)


def process_calendar_selection(bot,call):
    ret_data = (False,None)
    query = call
    (action,year,month,day) = separate_callback_data(query.data)
    curr = datetime.date(int(year), int(month), 1)
    if action == "СLIENT_ORDER_DATE_IGNORE":
        bot.answer_callback_query(callback_query_id= query.id)
    elif action == 'СLIENT_ORDER_DATE_DAY':
        if datetime.datetime(int(year), int(month), int(day)) < datetime.datetime.now():
            bot.answer_callback_query(call.id, text="Дата недоступна")
        else:
            bot.edit_message_text(text=query.message.text,
                chat_id=query.message.chat.id,
                message_id=query.message.message_id
                )
            ret_data = True,datetime.date(int(year),int(month),int(day))
    elif action == "СLIENT_ORDER_DATE_PREV-MONTH":
        pre = curr - datetime.timedelta(days=1)
        bot.edit_message_text(text=query.message.text,
            chat_id=query.message.chat.id,
            message_id=query.message.message_id,
            reply_markup=create_calendar(int(pre.year),int(pre.month)))
    elif action == "СLIENT_ORDER_DATE_NEXT-MONTH":
        ne = curr + datetime.timedelta(days=31)
        bot.edit_message_text(text=query.message.text,
            chat_id=query.message.chat.id,
            message_id=query.message.message_id,
            reply_markup=create_calendar(int(ne.year),int(ne.month)))
    else:
        bot.answer_callback_query(callback_query_id= query.id,text="Something went wrong!")
        # UNKNOWN
    return ret_data