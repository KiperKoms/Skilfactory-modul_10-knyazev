import telebot
from config import keys, TOKEN
from extensions import APIException, Convertermoney



def keyboard_keys(hid=None):
    keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    buttons = []
    for key in keys.keys():
        if key != hid:
            buttons.append(telebot.types.KeyboardButton(key))
    keyboard.add(*buttons)
    return keyboard


def keyboard_commands():
    keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    buttons = ['/convert', '/values', '/help']
    keyboard.add(*buttons)
    return keyboard


bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'help'])
def help(message: telebot.types.Message):
    text = f'Приветствую, {message.chat.username}!\n\
Я бот для конвертации валюты.\nСписок доступных для конвертации валют: /values\n\
Для начала работы воспользуйтесь командой /convert или напишите боту в следующем формате:\n\
<имя валюты> <в какую валюту перевести> <количество переводимой валюты>\n\
Доступные команды:\n/convert - конвертация.\n/values - список доступных валют.\n/help - помощь.'
    bot.reply_to(message, text, reply_markup=keyboard_commands())

@bot.message_handler(commands=['values'])
def values(message: telebot.types.Message):
    text = 'Доступные валюты:'
    for key in keys.keys():
        text = '\n'.join((text, key, ))
    bot.reply_to(message, text, reply_markup=keyboard_commands())

@bot.message_handler(commands=['convert'])
def convert(message: telebot.types.Message):
    text = 'Выберете валюту из которой конвертировать:'
    bot.send_message(message.chat.id, text, reply_markup=keyboard_keys())
    bot.register_next_step_handler(message, from_quote)


def from_quote(message: telebot.types.Message):
    quote = message.text
    text = 'Выберете валюту в которую конвертировать:'
    bot.send_message(message.chat.id, text, reply_markup=keyboard_keys(hid=quote))
    bot.register_next_step_handler(message, to_base, quote)


def to_base(message: telebot.types.Message, quote):
    base = message.text
    text = 'Напишите количество конвертируемой валюты:'
    bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(message, amount_base, quote, base)


def amount_base(message: telebot.types.Message, quote, base):
    amount_base = message.text.strip()
    try:
        total_base = Convertermoney.get_price(quote, base, amount_base)
    except APIException as e:
        bot.send_message(message.chat.id, f'Ошибка в конвертации:\n{e}', reply_markup=keyboard_commands())
    else:
        text = f'Стоимость одной еденицы валюты {quote} в валюте {base}: {total_base}\n\
{amount_base} {keys[quote]} = {round(float(total_base) * float(amount_base), 3)} {keys[base]}'
        bot.send_message(message.chat.id, text, reply_markup=keyboard_commands())


@bot.message_handler(content_types=['text', ])
def converter(message: telebot.types.Message):
    try:
        values = [i.capitalize() for i in message.text.split()]

        if len(values) != 3:
            raise APIException('Неверное количество параметров.')

        quote, base, amount = values
        total_base = Convertermoney.get_price(quote, base, amount)
    except APIException as e:
        bot.reply_to(message, f'Ошибка пользователя\n{e}', reply_markup=keyboard_commands())

    except Exception as e:
        bot.reply_to(message, f'Не удалось обработать команду\n{e}', reply_markup=keyboard_commands())
    else:
        text = f'Стоимость одной еденицы валюты {quote} в валюте {base}: {total_base}\n\
{amount} {keys[quote]} = {round(float(total_base) * float(amount), 3)} {keys[base]}'
        bot.send_message(message.chat.id, text)


bot.polling(none_stop=True)