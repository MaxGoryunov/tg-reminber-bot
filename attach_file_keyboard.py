from telebot import types

def attach_file_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    no = types.KeyboardButton("All attached")
    markup.add(no)
    return markup