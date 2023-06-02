import telebot
from telebot import types
import sql_query
import re

sq = sql_query.QueryTool()

auto_log = 'admin'
auto_pas = '0000'
logged_in = False
to_switch = []
to_del = []

bot = telebot.TeleBot('6031519919:AAFO0mD8GDuD3L8i9FFa1n9qJaNWMkfXP2E')

# ========================================= Start =========================================

@bot.message_handler(commands=['start'])
def start_bot(message):
    global to_switch, to_del
    rem_key = types.ReplyKeyboardRemove()
    bot.send_message(message.from_user.id,
                     "Приветствую!\nЯ – Ваш персональный помощник для работы с базой данных отеля _'Jewelry Nature'_",
                     reply_markup=rem_key,
                     parse_mode='Markdown')
    markup = types.InlineKeyboardMarkup()
    begin_btn = types.InlineKeyboardButton(text='Авторизация', callback_data='begin')
    markup.add(begin_btn)
    mes = bot.send_message(message.from_user.id,
                           'Для начала работы с ботом необходимо авторизироваться.',
                           reply_markup=markup)
    to_switch = [mes]

# ========================================= Connecting =========================================

@bot.callback_query_handler(func=lambda call: call.data == 'begin')
def begin_callback(call):
    if not sq.open_connection():
        markup = types.InlineKeyboardMarkup()
        begin_btn = types.InlineKeyboardButton(text='Повторить попытку', callback_data='begin')
        markup.add(begin_btn)
        bot.edit_message_text(
            chat_id=call.from_user.id,
            message_id=call.message.message_id,
            text='Не удалось подключиться к базе данных.',
            reply_markup=markup,
            parse_mode='Markdown')
    else:
        begin_callback(call)

# ========================================= Log in =========================================

@bot.callback_query_handler(func=lambda call: call.data == 'begin')
def begin_callback(call):
    mes = bot.send_message(call.from_user.id,
                           'Введите свой логин:',
                           parse_mode='html')
    to_del.append(mes.message_id)
    bot.register_next_step_handler(mes, get_login)

def get_login(message):
    user_login = message.text
    to_del.append(message.message_id)
    del_mes(message)
    mes = bot.send_message(message.from_user.id,
                           'Введите свой пароль:')
    to_del.append(mes.message_id)
    bot.register_next_step_handler(mes, get_pass, user_login)

def get_pass(message, user_login):
    global logged_in
    user_password = message.text
    to_del.append(message.message_id)
    del_mes(message)
    if auto_log == user_login and auto_pas == user_password:
        logged_in = True
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton('Начать работу', callback_data='main_menu')
        markup.row(btn1)
        bot.edit_message_text(
            chat_id=message.from_user.id,
            message_id=to_switch[0].message_id,
            text='Вы были успешно авторизованы!\nДавайте приступим к работе.',
            reply_markup=markup)
    else:
        markup = types.InlineKeyboardMarkup()
        begin_btn = types.InlineKeyboardButton(text='Повторить попытку', callback_data='begin')
        markup.row(begin_btn)
        mes = bot.send_message(message.from_user.id,
                               'Ошибка авторизации. Неверный логин или пароль.',
                               reply_markup=markup)
        to_del.append(mes.message_id)

# ========================================= Main Menu =========================================

@bot.message_handler(commands=['menu'], func=lambda call: logged_in)
@bot.callback_query_handler(func=lambda callback: callback.data == 'main_menu' and logged_in)
def main_menu(call):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Регистрация', callback_data='reg_mm')
    btn2 = types.InlineKeyboardButton('Бронирование', callback_data='bk_mm')
    btn3 = types.InlineKeyboardButton('Заселение', callback_data='ch_mm')
    btn4 = types.InlineKeyboardButton('Заказы', callback_data='ord_mm')
    btn5 = types.InlineKeyboardButton('Завершить работу', callback_data='end_mm')
    markup.row(btn1, btn2).row(btn3, btn4).row(btn5)
    mm_mes = '*Главное меню*\n\nВыберите необходимый раздел.'
    if type(call) is types.CallbackQuery:
        bot.edit_message_text(
            chat_id=call.from_user.id,
            message_id=call.message.message_id,
            text=mm_mes,
            reply_markup=markup,
            parse_mode='Markdown')
    else:
        bot.send_message(call.from_user.id,
                         mm_mes,
                         reply_markup=markup,
                         parse_mode='Markdown')

# ========================================= Func4All =========================================

def gen_markup(back):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('В главное меню', callback_data='main_menu')
    btn2 = types.InlineKeyboardButton('<< Назад', callback_data=back)
    markup.row(btn2, btn1)
    return markup

def del_mes(message):
    for i in range(len(to_del) - 1, -1, -1):
        bot.delete_message(message.from_user.id, to_del[i])
    to_del.clear()

def divide_str(text):
    div = re.split(", |\n|,", text)
    if len(div) > 1:
        return div
    else:
        return None

# ========================================= Register =========================================

@bot.callback_query_handler(func=lambda callback: callback.data.startswith('reg') and logged_in)
def reg_handler(call):
    global to_switch
    if call.data == 'reg_mm':
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton('Добавить профиль клиента', callback_data='reg_add_per')
        btn2 = types.InlineKeyboardButton('Добавить профиль компании', callback_data='reg_add_comp')
        btn3 = types.InlineKeyboardButton('<< Назад', callback_data='main_menu')
        markup.row(btn1).row(btn2).row(btn3)
        mes = bot.edit_message_text(
            chat_id=call.from_user.id,
            message_id=call.message.message_id,
            text='*Регистрация*\n\nВыберите необходимое действие.',
            reply_markup=markup,
            parse_mode='Markdown')
        to_switch = [mes]
    elif call.data == 'reg_add_per':
        mes = bot.send_message(
                  call.from_user.id,
                  'Введите данные через запятую, или каждое с новой строки\nДанные для ввода:\n\nИмя и фамилия\nНомер паспорта\nТелефонный номер\nЭлектранная почта')
        to_switch.append(mes)
        bot.register_next_step_handler(mes, reg_per_in)
    elif call.data == 'reg_add_comp':
        markup = gen_markup('reg_mm')
        bot.edit_message_text(
            chat_id=call.from_user.id,
            message_id=to_switch[0].message_id,
            text='Функция еще не добавлена',
            reply_markup=markup,
            parse_mode='Markdown')
        to_switch.clear()

def reg_per_in(message):
    user_in = message.text
    to_del.append(message.message_id)
    markup = gen_markup('reg_mm')
    divided = divide_str(user_in)
    if divided is not None and len(divided) == 4:
        flname, pas, phone, mail = (divided[i] for i in range(0, len(divided)))
        if sq.reg_per(flname, pas, phone, mail):
            del_mes(message)
            bot.edit_message_text(
                chat_id=message.from_user.id,
                message_id=to_switch[1].message_id,
                text=f'*Внесенные данные*\nИмя и фамилия: {flname}\nПаспорт: {pas}\nТелефонный номер: {phone}\nПочта: {mail}',
                parse_mode='Markdown')
            bot.send_message(
                message.from_user.id,
                'Данные были успешно внесены в базу данных!',
                reply_markup=markup,
                parse_mode='Markdown'
            )
        else:
            bot.send_message(
                message.from_user.id,
                'При внесении данных возникла ошибка.',
                reply_markup=markup,
                parse_mode='Markdown')
    else:
        bot.send_message(
            message.from_user.id,
            'Неверный ввод данных, повторите попытку.',
            reply_markup=markup,
            parse_mode='Markdown')
    to_switch.clear()
    to_del.clear()

# ========================================= Booking =========================================

@bot.callback_query_handler(func=lambda callback: callback.data.startswith('bk') and logged_in)
def bk_handler(call):
    global to_switch
    if call.data == 'bk_mm':
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton('Список активной брони', callback_data='bk_act')
        btn2 = types.InlineKeyboardButton('Отменить бронь', callback_data='bk_reject')
        btn3 = types.InlineKeyboardButton('<< Назад', callback_data='main_menu')
        markup.row(btn1).row(btn2).row(btn3)
        mes = bot.edit_message_text(
            chat_id=call.from_user.id,
            message_id=call.message.message_id,
            text='*Бронирование*\n\nВыберите необходимое действие.',
            reply_markup=markup,
            parse_mode='Markdown')
        to_switch = [mes]
    elif call.data == 'bk_act':
        bk_active = sq.bk_active()
        markup = gen_markup('bk_mm')
        if bk_active is not None:
            out = ''
            corp = None
            for i in range(0, len(bk_active)):
                if bk_active[i][0] == '':
                    if corp is None:
                        corp = bk_active[i][1]
                        out += (f'\nКомпания: {corp}\nДаты брони: %s – %s\nПредоплата за комнаты: ${bk_active[i][2]}',
                                bk_active[i][3].replace('-', '.'), bk_active[i][4].replace('-', '.'))
                        continue
                    if corp == bk_active[i][1]:
                        out += f', ${bk_active[i][2]}'
                    else:
                        corp = bk_active[i][1]
                        out += (f'\nКомпания: {corp}\nДаты брони: %s – %s\nПредоплата за комнаты: ${bk_active[i][2]}',
                                bk_active[i][3].replace('-', '.'), bk_active[i][4].replace('-', '.'))
                else:
                    out += (f'\nИмя и фамилия: {bk_active[i][0]}\nДата брони: %s – %s\nПредоплата за комнату: ${bk_active[i][2]}',
                            bk_active[i][3].replace('-', '.'), bk_active[i][4].replace('-', '.'))
            bot.edit_message_text(
                chat_id=call.from_user.id,
                message_id=to_switch[0].message_id,
                text=f'*Список активной брони*\n{out}',
                reply_markup=markup,
                parse_mode='Markdown')
        else:
            bot.edit_message_text(
                chat_id=call.from_user.id,
                message_id=to_switch[0].message_id,
                text='При выводе данных произошла ошибка.',
                reply_markup=markup,
                parse_mode='Markdown')
        to_switch.clear()
    elif call.data == 'bk_reject':
        mes = bot.send_message(
                  call.from_user.id,
                  'Введите данные через запятую, или каждое с новой строки\nДанные для ввода:\n\nТип пользователя (Компания / Клиент)\nИНН / Имя и фамилия\nДата начала брони (В формате год-месяц-день)')
        to_switch.append(mes)
        bot.register_next_step_handler(mes, bk_rej_in)

def bk_rej_in(message):
    user_in = message.text
    to_del.append(message.message_id)
    markup = gen_markup('bk_mm')
    divided = divide_str(user_in)
    if divided is not None and len(divided) == 3:
        user_type, name, date = (divided[i] for i in range(0, len(divided)))
        if sq.bk_change(user_type, name, date):
            del_mes(message)
            if name.isdigit():
                abc = 'ИНН'
            else:
                abc = 'Имя и фамилия'
            bot.edit_message_text(
                chat_id=message.from_user.id,
                message_id=to_switch[1].message_id,
                text=f'*Удаление брони*\nТип пользователя: {user_type}\n{abc}: {name}\nДата начала брони: {date}',
                parse_mode='Markdown')
            bot.send_message(
                message.from_user.id,
                'Бронь была успешно удалена!',
                reply_markup=markup,
                parse_mode='Markdown'
            )
        else:
            bot.send_message(
                message.from_user.id,
                'При удалении возникла ошибка.',
                reply_markup=markup,
                parse_mode='Markdown')
    else:
        bot.send_message(
            message.from_user.id,
            'Неверный ввод данных, повторите попытку.',
            reply_markup=markup,
            parse_mode='Markdown')
    to_switch.clear()
    to_del.clear()

# ========================================= Check in =========================================

@bot.callback_query_handler(func=lambda callback: callback.data.startswith('ch') and logged_in)
def ch_handler(call):
    global to_switch
    if call.data == 'ch_mm':
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton('Сегодняшнее заселение', callback_data='ch_today')
        btn2 = types.InlineKeyboardButton('Свободные комнаты', callback_data='ch_free')
        btn3 = types.InlineKeyboardButton('Список услуг', callback_data='ch_serv')
        btn4 = types.InlineKeyboardButton('<< Назад', callback_data='main_menu')
        markup.row(btn1).row(btn2, btn3).row(btn4)
        mes = bot.edit_message_text(
            chat_id=call.from_user.id,
            message_id=call.message.message_id,
            text='*Заселение*\n\nВыберите необходимое действие.',
            reply_markup=markup,
            parse_mode='Markdown')
        to_switch = [mes]
    elif call.data == 'ch_today':
        ch_today = sq.ch_today()
        markup = gen_markup('ch_mm')
        if ch_today is not None:
            out = ''
            for i in range(0, len(ch_today)):
                out += f'Имя и фамилия: {ch_today[i][0]}\nТелефон: {ch_today[i][1]}\nКорпус и комната: {ch_today[i][3]}, {ch_today[i][2]}\n\n'
            bot.edit_message_text(
                chat_id=call.from_user.id,
                message_id=to_switch[0].message_id,
                text=f'*Список сегодняшнего заселения*\n\n{out}',
                reply_markup=markup,
                parse_mode='Markdown')
        else:
            bot.edit_message_text(
                chat_id=call.from_user.id,
                message_id=to_switch[0].message_id,
                text='При выводе данных произошла ошибка.',
                reply_markup=markup,
                parse_mode='Markdown')
        to_switch.clear()
    elif call.data == 'ch_free':
        ch_today = sq.ch_free()
        markup = gen_markup('ch_mm')
        if ch_today is not None:
            housing = ch_today[0][1]
            out = f'Корпус: {ch_today[0][1]}\nКомнаты: {ch_today[0][0]}'

            for i in range(1, len(ch_today)):
                if ch_today[i][1] == housing:
                    out += f', {ch_today[i][0]}'
                else:
                    housing = ch_today[i][1]
                    out += f'\n\nКорпус: {ch_today[i][1]}\nКомнаты: {ch_today[i][0]}'
            bot.edit_message_text(
                chat_id=call.from_user.id,
                message_id=to_switch[0].message_id,
                text=f'*Свободные для заселения комнаты*\n\n{out}',
                reply_markup=markup,
                parse_mode='Markdown')
        else:
            bot.edit_message_text(
                chat_id=call.from_user.id,
                message_id=to_switch[0].message_id,
                text='При выводе данных произошла ошибка.',
                reply_markup=markup,
                parse_mode='Markdown')
        to_switch.clear()
    elif call.data == 'ch_serv':
        ch_serv = sq.ch_serv()
        markup = gen_markup('ch_mm')
        if ch_serv is not None:
            housing = ch_serv[0][2]
            out = f'Корпус: {ch_serv[0][2]}\nДоступный сервис, цена:\n'
            for i in range(0, len(ch_serv)):
                if ch_serv[i][2] == housing:
                    out += f'{ch_serv[i][0]}, ${ch_serv[i][1]}\n'
                else:
                    housing = ch_serv[i][2]
                    out += f'\nКорпус: {ch_serv[i][2]}\nДоступный сервис, цена:\n'
                    out += f'{ch_serv[i][0]}, ${ch_serv[i][1]}\n'
            bot.edit_message_text(
                chat_id=call.from_user.id,
                message_id=to_switch[0].message_id,
                text=f'*Список доступных услуг*\n\n{out}',
                reply_markup=markup,
                parse_mode='Markdown')
        else:
            bot.edit_message_text(
                chat_id=call.from_user.id,
                message_id=to_switch[0].message_id,
                text='При выводе данных произошла ошибка.',
                reply_markup=markup,
                parse_mode='Markdown')
        to_switch.clear()

# ========================================= Orders =========================================

@bot.callback_query_handler(func=lambda callback: callback.data.startswith('ord') and logged_in)
def ord_handler(call):
    global to_switch
    if call.data == 'ord_mm':
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton('Просмотр заказов', callback_data='ord_zak')
        btn2 = types.InlineKeyboardButton('Задолженность', callback_data='ord_duty')
        btn3 = types.InlineKeyboardButton('Добавить заказ', callback_data='ord_add')
        btn4 = types.InlineKeyboardButton('Удалить заказ', callback_data='ord_del')
        btn5 = types.InlineKeyboardButton('<< Назад', callback_data='main_menu')
        markup.row(btn1, btn2).row(btn3, btn4).row(btn5)
        mes = bot.edit_message_text(
            chat_id=call.from_user.id,
            message_id=call.message.message_id,
            text='*Заказы*\n\nВыберите необходимое действие.',
            reply_markup=markup,
            parse_mode='Markdown')
        to_switch = [mes]
    elif call.data == 'ord_zak':
        mes = bot.send_message(
                  call.from_user.id,
                  'Введите ID заселения, по которому необходимо просмотреть заказы:')
        to_switch.append(mes)
        bot.register_next_step_handler(mes, ord_zak_in)
    elif call.data == 'ord_duty':
        mes = bot.send_message(
                  call.from_user.id,
                  'Введите имя и фамилию человека, задолженность которого необходимо узнать:')
        to_switch.append(mes)
        bot.register_next_step_handler(mes, ord_duty_in)
    elif call.data == 'ord_add':
        mes = bot.send_message(
                  call.from_user.id,
                  'Введите данные через запятую, или каждое с новой строки\nДанные для ввода:\n\nИмя и фамилия\nНазвание услуги\nКоличетсво\nСтатус оплаты (Оплачено / Не оплачено)')
        to_switch.append(mes)
        bot.register_next_step_handler(mes, ord_add_in)
    elif call.data == 'ord_del':
        mes = bot.send_message(
                  call.from_user.id,
                  'Введите данные через запятую, или каждое с новой строки\nДанные для ввода:\n\nИмя и фамилия\nНазвание услуги')
        to_switch.append(mes)
        bot.register_next_step_handler(mes, ord_add_in)

def ord_zak_in(message):
    user_in = message.text
    to_del.append(message.message_id)
    markup = gen_markup('ord_mm')
    if user_in.isdigit():
        ord_zak = sq.ord_zak(user_in)
        if ord_zak is not None:
            del_mes(message)
            if ord_zak == []:
                out = 'Клиент не совершал заказов'
            else:
                out = f'ID заселения: {user_in}\nИмя клиента: {ord_zak[0][3]}\nКорпус, комната: {ord_zak[0][1]}, {ord_zak[0][2]}\nЗаказы, количество и статус оплаты: '
                for i in range(0, len(ord_zak)):
                    p_stat = ('Оплачено' if ord_zak[i][6] else 'Не оплачено')
                    out += f'{ord_zak[i][4]} {ord_zak[i][5]}, {p_stat}\n'
            bot.edit_message_text(
                chat_id=message.from_user.id,
                message_id=to_switch[1].message_id,
                text=f'*Список заказов*\n{out}',
                parse_mode='Markdown')
            bot.send_message(
                message.from_user.id,
                'Список заказов был успешно выведен!',
                reply_markup=markup,
                parse_mode='Markdown')
        else:
            bot.send_message(
                message.from_user.id,
                'При выводе данных возникла ошибка.',
                reply_markup=markup,
                parse_mode='Markdown')
    else:
        bot.send_message(
            message.from_user.id,
            'Неверный ввод данных, повторите попытку.',
            reply_markup=markup,
            parse_mode='Markdown')
    to_switch.clear()
    to_del.clear()

def ord_duty_in(message):
    user_in = message.text
    to_del.append(message.message_id)
    markup = gen_markup('ord_mm')
    if len(user_in.split(' ')) == 2:
        ord_duty = sq.ord_duty(user_in)
        if ord_duty is not None:
            del_mes(message)
            out = f'Имя клиента: {user_in}\nТелефон клиента: {ord_duty[0][0]}\nСумма долга: ${ord_duty[0][1]}'
            bot.edit_message_text(
                chat_id=message.from_user.id,
                message_id=to_switch[1].message_id,
                text=f'*Задолженность клиента*\n{out}',
                parse_mode='Markdown')
            bot.send_message(
                message.from_user.id,
                'Задолженность клиента была успешно выведена!',
                reply_markup=markup,
                parse_mode='Markdown')
        else:
            bot.send_message(
                message.from_user.id,
                'При выводе данных возникла ошибка.',
                reply_markup=markup,
                parse_mode='Markdown')
    else:
        bot.send_message(
            message.from_user.id,
            'Неверный ввод данных, повторите попытку.',
            reply_markup=markup,
            parse_mode='Markdown')
    to_switch.clear()
    to_del.clear()

def ord_add_in(message):
    user_in = message.text
    to_del.append(message.message_id)
    markup = gen_markup('ord_mm')
    divided = divide_str(user_in)
    if divided is not None and len(divided) == 4:
        flname, serv, quantity, stat = (divided[i] for i in range(0, len(divided)))
        if sq.ord_add(flname, serv, (1 if stat == 'Оплачено' or stat == 'оплачено' else 0), quantity):
            del_mes(message)
            out = f'Имя клиента: {flname}\nНазвание услуги, количество и статус оплаты: {serv}, {quantity}, {stat}'
            bot.edit_message_text(
                chat_id=message.from_user.id,
                message_id=to_switch[1].message_id,
                text=f'*Добавление заказа*\n{out}',
                parse_mode='Markdown')
            bot.send_message(
                message.from_user.id,
                'Заказ был успешно добавлен!',
                reply_markup=markup,
                parse_mode='Markdown')
        else:
            bot.send_message(
                message.from_user.id,
                'При выводе данных возникла ошибка.',
                reply_markup=markup,
                parse_mode='Markdown')
    else:
        bot.send_message(
            message.from_user.id,
            'Неверный ввод данных, повторите попытку.',
            reply_markup=markup,
            parse_mode='Markdown')
    to_switch.clear()
    to_del.clear()

def ord_del_in(message):
    user_in = message.text
    to_del.append(message.message_id)
    markup = gen_markup('ord_mm')
    divided = divide_str(user_in)
    if divided is not None and len(divided) == 2:
        flname, serv = (divided[i] for i in range(0, len(divided)))
        if sq.ord_del(flname, serv):
            del_mes(message)
            out = f'Имя клиента: {flname}\nНазвание услуги{serv}'
            bot.edit_message_text(
                chat_id=message.from_user.id,
                message_id=to_switch[1].message_id,
                text=f'*Удаление последнего заказа*\n{out}',
                parse_mode='Markdown')
            bot.send_message(
                message.from_user.id,
                'Последний заказ пользователя был удален!',
                reply_markup=markup,
                parse_mode='Markdown')
        else:
            bot.send_message(
                message.from_user.id,
                'При выводе данных возникла ошибка.',
                reply_markup=markup,
                parse_mode='Markdown')
    else:
        bot.send_message(
            message.from_user.id,
            'Неверный ввод данных, повторите попытку.',
            reply_markup=markup,
            parse_mode='Markdown')
    to_switch.clear()
    to_del.clear()

# ========================================= End =========================================

@bot.message_handler(commands=['exit'], func=lambda call: logged_in)
@bot.callback_query_handler(func=lambda callback: callback.data == 'end_mm' and logged_in)
def end_handler(call):
    global logged_in
    end_mes = '*Завершение работы.*\n\nХорошо поработали сегодня! Соединение с базой данных было успешно разорвано. До новых встреч.'
    if type(call) is types.CallbackQuery:
        bot.edit_message_text(
            chat_id=call.from_user.id,
            message_id=call.message.message_id,
            text=end_mes,
            parse_mode='Markdown')
    else:
        bot.send_message(call.from_user.id,
                         end_mes,
                         parse_mode='Markdown')
    sq.close_connection()
    logged_in = False

# ========================================= Not logged =========================================

@bot.message_handler(commands=['menu', 'exit'], func=lambda call: not logged_in)
def not_logged(message):
    bot.send_message(message.from_user.id,
                     'Невозможно выполнить команду. Вы еще не авторизованы. Для авторизации воспользуйтесь командой /start',
                     parse_mode='Markdown')

# ========================================= Start up bot =========================================

if __name__ == "__main__":
    bot.infinity_polling()
