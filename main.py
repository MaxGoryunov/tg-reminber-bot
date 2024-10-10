import io
from time import sleep
import threading
import uvicorn
import telebot
from telebot import types
from telebot.types import ReplyKeyboardRemove, CallbackQuery
from telebot_calendar import Calendar, CallbackData, ENGLISH_LANGUAGE
from attach_file_keyboard import attach_file_keyboard
import datetime
import config
from models import Notification
from utils import store_notification, store_db_entry, get_awaited_notifications, show_notification, \
    awaited_notifications_options, print_awaited_notifications, modify_notification_options, change_title, \
    get_notification_by_id, get_notification_files, download_file, change_datetime, delete_notification, \
    change_interval, make_one_time, make_recurring, mark_as_sent, update_files_on_disk, change_one_time_title, \
    change_one_time_datetime, update_one_time_files_on_disk, offset_recurring_notification_by_interval, \
    offset_disk_folder, get_sent_notifications, sent_notifications_options, mark_as_awaited, print_sent_notifications

token = config.BOT_TOKEN
bot = telebot.TeleBot(token)
glob_chat = {
    'message': None
}

calendar = Calendar(language=ENGLISH_LANGUAGE)
calendar_1_callback = CallbackData("calendar_1", "action", "year", "month", "day")

start = datetime.datetime.now()


def show_completed_nftn(message, nftn: Notification):
    bot.send_message(message.chat.id, "<b>You have a notification</b>: ", parse_mode='HTML')
    msg = bot.send_message(message.chat.id, show_notification(nftn))
    print("nftn description = ", msg.text)
    files = get_notification_files(message, nftn)
    for file in files:
        file_content = download_file(file['id'])
        file_name = file['name']
        # создаем объект io.BytesIO из скачанного файла
        file_io = io.BytesIO(file_content)
        file_io.name = file_name
        bot.send_document(message.chat.id, document=file_io)
    bot.send_message(message.chat.id, "All attached files sent.")


def notification_loop():
    prev = start
    message = None
    
    while True:
        sleep(5)
        print("5 secs have passed")
        # if glob_chat['message'] is not None:
        #     print("is not none")
        #     message = glob_chat['message']
        #     notifications = get_awaited_notifications(message)
        #     for nftn in notifications:
        #         if nftn.is_recurring and nftn.notification_datetime < datetime.datetime.now():
        #             show_completed_nftn(message, nftn)
        #             offset_recurring_notification_by_interval(nftn)
        #         elif (not nftn.is_recurring) and nftn.notification_datetime < datetime.datetime.now():
        #             print("here")
        #             show_completed_nftn(message, nftn)
        #             mark_as_sent(nftn.id)


@bot.message_handler(commands=['start'])
def start_message(message):
    glob_chat['message'] = message
    bot.send_message(
        message.chat.id,
        "Hi! This bot can help you with reminding about different events and"
        + " materials needed for them"
    )
    menu_options(message)

@bot.message_handler(commands=["menu"])
def menu_options(message):
    print("glob chat id = ", glob_chat['message'].chat.id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    create = types.KeyboardButton("Create a notification")
    awaited = types.KeyboardButton("View awaited notifications")
    view = types.KeyboardButton("View sent notifications")
    markup.add(create, awaited, view)
    msg = bot.send_message(
        message.chat.id,
        "You are in the main menu\n" +
        "What would you like to do?",
        reply_markup=markup
    )
    print("msg for message reply", msg.text)
    bot.register_next_step_handler(msg, message_reply)


def view_awaited_notifications(message):
    notifications = get_awaited_notifications(message)
    # print(notifications[0].chat_id)
    txt = print_awaited_notifications(notifications)
    bot.send_message(
        message.chat.id,
        txt
    )
    msg = bot.send_message(
        message.chat.id,
        "What would you like to do?",
        reply_markup=awaited_notifications_options()
    )
    bot.register_next_step_handler(msg, awaited_nots_reply)


def message_reply(message):
    print("inside message reply message ", message.text)
    if message.text == "Create a notification":
        print("Chosen create a notification")
        now = datetime.datetime.now()  # Get the current date
        bot.send_message(
            message.chat.id,
            "Select a date",
            reply_markup=calendar.create_calendar(
                name=calendar_1_callback.prefix,
                year=now.year,
                month=now.month,  # Specify the NAME of your calendar
            ),

        )
    elif message.text == "View awaited notifications":
        view_awaited_notifications(message)
    elif message.text == "View sent notifications":
        view_sent_notifications(message)


def view_sent_notifications(message):
    notifications = get_sent_notifications(message)
    txt = print_sent_notifications(notifications)
    bot.send_message(message.chat.id, txt)
    msg = bot.send_message(
        message.chat.id,
        "What would you like to do?",
        reply_markup=sent_notifications_options()
    )
    bot.register_next_step_handler(msg, sent_ntfns_reply)


def sent_ntfns_reply(message):
    if message.text == "Go back to the menu":
        menu_options(message)
    elif message.text == "Mark as awaited":
        notifications = get_sent_notifications(message)
        msg = bot.send_message(
            message.chat.id,
            "Choose the index of a notification you want to return to awaited: \n" +
            print_awaited_notifications(notifications)
        )
        bot.register_next_step_handler(msg, pre_ask_new_datetime, notifications)


def awaited_nots_reply(message):
    print("Awaited_nots text = ", message.text)
    if message.text == "Go back to the menu":
        menu_options(message)
    elif message.text == "Modify a notification":
        notifications = get_awaited_notifications(message)
        msg = bot.send_message(
            message.chat.id,
            "Choose the index of a notification you would like to change: \n" +
            print_awaited_notifications(
                notifications
            )
        )
        # print("awaited modify msg text = ", msg.text)
        bot.register_next_step_handler(msg, pre_show_notification_data, notifications)


def pre_ask_new_datetime(message, notifications):
    n_ind = int(message.text)
    n_id = notifications[n_ind - 1].id
    ask_new_datetime(message, n_id)


def pre_show_notification_data(message, notifications):
    print("pre text = ", message.text)
    n_ind = int(message.text)
    n_id = notifications[n_ind - 1].id
    show_notification_data(message, n_id)


def ask_new_datetime(message, n_id):
    notification = get_notification_by_id(n_id)
    msg = bot.send_message(
        message.chat.id,
        "Enter new datetime in the format dd.mm.yyyy HH:MM"
    )
    bot.register_next_step_handler(msg, save_as_awaited, notification)


def save_as_awaited(message, nftn: Notification):
    dt = datetime.datetime.strptime(message.text, "%d.%m.%Y %H:%M")
    change_datetime(message, nftn, dt)
    mark_as_awaited(nftn.id)
    view_awaited_notifications(message)


def show_notification_data(message, n_id):
    print("show not message = ", message.text)
    notification = get_notification_by_id(n_id)
    msg = bot.send_message(message.chat.id, show_notification(notification))
    print("nftn description = ", msg.text)
    files = get_notification_files(message, notification)
    for file in files:
        file_content = download_file(file['id'])
        file_name = file['name']
        # создаем объект io.BytesIO из скачанного файла
        file_io = io.BytesIO(file_content)
        file_io.name = file_name
        bot.send_document(message.chat.id, document=file_io)

    msg = bot.send_message(
        message.chat.id,
        "What would you like to do with the chosen notification?",
        reply_markup=modify_notification_options(notification)
    )
    bot.register_next_step_handler(msg, modify_notification, notification)


def local_change_title(message, nftn: Notification):
    print("new title = ", message.text)
    change_title(nftn.id, message.text)
    show_notification_data(message, nftn.id)


def local_change_one_time_title(message, nftn: Notification):
    change_one_time_title(message, nftn, message.text)
    view_awaited_notifications(message)


def local_change_datetime(message, nftn: Notification):
    print("new datetime = ", message.text)
    dt = datetime.datetime.strptime(message.text, "%d.%m.%Y %H:%M")
    change_datetime(message, nftn, dt)
    show_notification_data(message, nftn.id)


def local_change_one_time_datetime(message, nftn: Notification):
    dt = datetime.datetime.strptime(message.text, "%d.%m.%Y %H:%M")
    change_one_time_datetime(message, nftn, dt)
    view_awaited_notifications(message)


def local_change_interval(message, nftn: Notification):
    print("new interval = ", message.text)
    change_interval(nftn.id, int(message.text))
    show_notification_data(message, nftn.id)
    # bot.register_next_step_handler(message, show_notification_data, nftn.id)


def modify_notification(message, nftn: Notification):
    if message.text == "Change title" or message.text == "Change recurring title":
        msg = bot.send_message(
            message.chat.id,
            "Enter new title for this notification"
        )
        bot.register_next_step_handler(msg, local_change_title, nftn)
    elif message.text == "Change datetime" or message.text == "Change recurring datetime":
        msg = bot.send_message(
            message.chat.id,
            "Enter new datetime in the format dd.mm.yyyy HH:MM"
        )
        bot.register_next_step_handler(msg, local_change_datetime, nftn)
    elif message.text == "Delete notification" or message.text == "Delete all-time notifications":
        delete_notification(message, nftn)
        view_awaited_notifications(message)
    elif message.text == "Delete next notification":
        offset_disk_folder(message, nftn)
        offset_recurring_notification_by_interval(nftn)
        view_awaited_notifications(message)
    elif message.text == "Change interval":
        msg = bot.send_message(
            message.chat.id,
            "Enter new interval in days"
        )
        bot.register_next_step_handler(msg, local_change_interval, nftn)
    elif message.text == "Make one-time":
        make_one_time(nftn.id)
        show_notification_data(message, nftn.id)
        # bot.register_next_step_handler(message, show_notification_data, nftn.id)
    elif message.text == "Make recurring":
        make_recurring(nftn.id)
        show_notification_data(message, nftn.id)
        # bot.register_next_step_handler(message, show_notification_data, nftn.id)
    elif message.text == "Mark as sent":
        mark_as_sent(nftn.id)
        view_awaited_notifications(message)
    elif message.text == "Change recurring files" or message.text == "Change attached files":
        print("Changing regular files")
        msg = bot.send_message(
            message.chat.id,
            "Attach required documents one by one, "
            + "enter 'All attached' when all documents are attached.",
            reply_markup=attach_file_keyboard()
        )
        docs = []
        bot.register_next_step_handler(msg, change_files_loop, docs, nftn)
    elif message.text == "Change one-time title":
        msg = bot.send_message(
            message.chat.id,
            "Send new title for a one-time notification based on this recurring notification"
        )
        bot.register_next_step_handler(msg, local_change_one_time_title, nftn)
    elif message.text == "Change one-time datetime":
        msg = bot.send_message(
            message.chat.id,
            "Enter new one-time notification datetime in the format dd.mm.yyyy HH:MM"
        )
        bot.register_next_step_handler(msg, local_change_one_time_datetime, nftn)
    elif message.text == "Change one-time files":
        msg = bot.send_message(
            message.chat.id,
            "Attach required documents for new one-time notification one by one, "
            + "enter 'All attached' when all documents are attached.",
            reply_markup=attach_file_keyboard()
        )
        docs = []
        bot.register_next_step_handler(msg, change_one_time_files_loop, docs, nftn)
    elif message.text == "Back to awaited notifications":
        view_awaited_notifications(message)


def change_files_loop(message, docs, nftn: Notification):
    if message.text == "All attached":
        res = update_files_on_disk(bot, message, nftn, docs)

        view_awaited_notifications(message)
        # bot.register_next_step_handler(message, view_awaited_notifications)
    else:
        docs = docs + [message.document]
        msg = bot.send_message(message.chat.id, "Attach another file?", reply_markup=attach_file_keyboard())
        bot.register_next_step_handler(msg, change_files_loop, docs, nftn)


def change_one_time_files_loop(message, docs, nftn: Notification):
    if message.text == "All attached":
        res = update_one_time_files_on_disk(bot, message, nftn, docs)
        if res:
            bot.send_message(message.chat.id, "Attached files changed")
        else:
            bot.send_message(message.chat.id, "Something went wrong")
        view_awaited_notifications(message)
        # bot.register_next_step_handler(message, view_awaited_notifications)
    else:
        docs = docs + [message.document]
        msg = bot.send_message(message.chat.id, "Attach another file?", reply_markup=attach_file_keyboard())
        bot.register_next_step_handler(msg, change_one_time_files_loop, docs, nftn)


@bot.callback_query_handler(
    func=lambda call: call.data.startswith(calendar_1_callback.prefix),
)
def callback_inline(call: CallbackQuery):
    """
    Обработка inline callback запросов
    :param call:
    :return:
    """

    # At this point, we are sure that this calendar is ours. So we cut the line by the separator of our calendar
    name, action, year, month, day = call.data.split(calendar_1_callback.sep)
    # Processing the calendar. Get either the date or None if the buttons are of a different type
    date = calendar.calendar_query_handler(
        bot=bot, call=call, name=name, action=action, year=year, month=month, day=day
    )
    # There are additional steps. Let's say if the date DAY is selected, you can execute your code. I sent a message.
    if action == "DAY":
        msg = bot.send_message(
            chat_id=call.from_user.id,
            text=f"You have chosen {date.strftime('%d.%m.%Y')}\n"
            + "Enter desired time in the format HH:MM",
            reply_markup=ReplyKeyboardRemove(),
        )
        bot.register_next_step_handler(msg, read_title, date)
        # print(f"{calendar_1_callback}: Day: {date.strftime('%d.%m.%Y')}")
    elif action == "CANCEL":
        bot.send_message(
            chat_id=call.from_user.id,
            text="Cancellation",
            reply_markup=ReplyKeyboardRemove(),
        )
        print(f"{calendar_1_callback}: Cancellation")
# @bot.message_handler(commands=["create_event"])


def read_title(message, date):
    hour, minute = message.text.split(":")
    msg = bot.send_message(message.chat.id, "Enter the title of your event")
    bot.register_next_step_handler(msg, attach_files_initial, date, hour, minute)


def attach_files_initial(message, date, hour, minute):
    title = message.text
    msg = bot.send_message(
        message.chat.id,
        "Attach required documents one by one, "
        + "enter 'All attached' when all documents are attached.",
        reply_markup=attach_file_keyboard()
    )
    docs = []
    bot.register_next_step_handler(msg, attach_files_loop, date, hour, minute, title, docs)


def attach_files_loop(message, date, hour, minute, title, docs):
    # print(docs)
    files = [doc.file_name for doc in docs]
    if message.text == "All attached":
        store_db_entry(message, date, hour, minute, title)
        store_notification(bot, message, date, hour, minute, docs)
        bot.send_message(
            message.chat.id,
            f"Your title: {title}\n"
            + f"Date: {date.strftime('%d.%m.%Y')}, time: {hour}:{minute}\n"
            + "\n".join(files)
        )
        menu_options(message)
    else:
        docs = docs + [message.document]
        msg = bot.send_message(message.chat.id, "Attach another file?", reply_markup=attach_file_keyboard())
        bot.register_next_step_handler(msg, attach_files_loop, date, hour, minute, title, docs)

# bot.infinity_polling()
# notification_loop()

if __name__ == '__main__':
    threading.Thread(
        target=bot.infinity_polling,
        name="bot infinity polling",
        daemon=True
    ).start()
    threading.Thread(
        target=notification_loop,
        name="notification loop",
        daemon=True
    ).start()

    uvicorn.run('server:app', host='0.0.0.0', port=3000, reload=True)
