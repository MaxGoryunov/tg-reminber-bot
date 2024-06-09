import os.path
import io
import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload, MediaIoBaseDownload
from sqlalchemy.orm import Session
from telebot import types

from models import Notification, engine
from sqlalchemy import update, insert, select, or_, delete, desc, and_
from datetime import datetime, timedelta

SCOPES = ["https://www.googleapis.com/auth/drive"]


def awaited_notifications_options():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    modify = types.KeyboardButton("Modify a notification")
    back = types.KeyboardButton("Go back to the menu")
    markup.add(modify, back)
    return markup


def sent_notifications_options():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    to_awaited = types.KeyboardButton("Mark as awaited")
    back = types.KeyboardButton("Go back to the menu")
    markup.add(to_awaited, back)
    return markup


def modify_notification_options(nftn: Notification):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if nftn.is_recurring:
        one_title = types.KeyboardButton("Change one-time title")
        rec_title = types.KeyboardButton("Change recurring title")
        one_time = types.KeyboardButton("Change one-time datetime")
        rec_time = types.KeyboardButton("Change recurring datetime")
        one_files = types.KeyboardButton("Change one-time files")
        rec_files = types.KeyboardButton("Change recurring files")
        one_delete = types.KeyboardButton("Delete next notification")
        rec_delete = types.KeyboardButton("Delete all-time notifications")
        interval = types.KeyboardButton("Change interval")
        make_one = types.KeyboardButton("Make one-time")
        markup.row(one_title, rec_title)
        markup.row(one_time, rec_time)
        markup.row(one_files, rec_files)
        markup.row(one_delete, rec_delete)
        markup.row(interval, make_one)
    else:
        title = types.KeyboardButton("Change title")
        time = types.KeyboardButton("Change datetime")
        files = types.KeyboardButton("Change attached files")
        delete = types.KeyboardButton("Delete notification")
        make_recurring = types.KeyboardButton("Make recurring")
        make_sent = types.KeyboardButton("Mark as sent")
        markup.row(title, time)
        markup.row(files, delete)
        markup.row(make_recurring, make_sent)
    markup.row(types.KeyboardButton("Back to awaited notifications"))
    # markup.row(files, delete)
    # markup.row(make_recurring, make_one_time)
    return markup


def print_awaited_notifications(notifications):
    txt = "Awaited notifications:\n"
    i = 1
    for notification in notifications:
        txt = txt + f"{i}: {show_notification(notification)} \n"
        i = i + 1
    return txt


def print_sent_notifications(notifications):
    txt = "Sent notifications:\n"
    i = 1
    for notification in notifications:
        txt = txt + f"{i}: {show_notification(notification)} \n"
        i = i + 1
    return txt


def upload_to_google_drive(file_content, file_name, folder_id, service):
    """Загружает файл на Google Диск."""
    file_metadata = {
        'name': file_name,
        'parents': [folder_id],
    }
    media = MediaIoBaseUpload(io.BytesIO(file_content), mimetype='application/octet-stream', resumable=True)
    service.files().create(body=file_metadata, media_body=media, fields='id').execute()


def form_datetime(date, hour, minute):
    return f"{date.strftime('%d.%m.%Y')} {hour}:{minute}:00"


def get_creds():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds


def store_notification(bot, message, date, hour, minute,  docs):
    """Shows basic usage of the Drive v3 API.
      Prints the names and ids of the first 10 files the user has access to.
      """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    # print("one")
    try:
        service = build("drive", "v3", credentials=creds)

        # Создание папки
        # file_metadata = {
        #     'name': FOLDER_NAME,
        #     'mimeType': 'application/vnd.google-apps.folder'
        # }
        # folder = service.files().create(body=file_metadata, fields='id').execute()
        # folder_id = folder.get('id')
        #
        # # Загрузка файла в папку
        # media = MediaFileUpload(FILE_PATH, mimetype='text/plain')
        # file_metadata = {
        #     'name': 'file.txt',
        #     'parents': [folder_id]
        # }
        # file = service.files().create(body=file_metadata, media_body=media,
        #                               fields='id').execute()
        # print(f'File ID: {file.get("id")} was uploaded to folder {FOLDER_NAME}')
        # print("hello-------")
        # Call the Drive v3 API
        print(f"chat id = {message.chat.id}")
        dt = form_datetime(date, hour, minute)
        # results = service.files().list(
        #     q=f"mimeType='application/vnd.google-apps.folder' and name='{message.chat.id} {dt}'",
        #     spaces='drive',
        #     fields='nextPageToken, files(id, name)'
        # ).execute()
        # items = results.get('files', [])
        # if not items:
        #     print(f"Creating a folder {message.chat.id}")
        #     # Создание папки
        #     file_metadata = {
        #         'name': f"{message.chat.id} {dt}",
        #         'mimeType': 'application/vnd.google-apps.folder'
        #     }
        #     folder = service.files().create(body=file_metadata, fields='id').execute()
        #     folder_id = folder.get("id")
        # else:
        #     print(items)
        #     folder_id = items[0]["id"]
        #     print(folder_id)
        # print(folder_id)
        print(f"{message.chat.id} {dt}")
        file_metadata = {
            'name': f"{message.chat.id} {dt}",
            'mimeType': 'application/vnd.google-apps.folder',
        }
        file_folder = service.files().create(body=file_metadata, fields='id').execute()
        ff_id = file_folder.get("id")
        for doc in docs:
            # Получаем информацию о файле
            file_info = bot.get_file(doc.file_id)
            file_name = doc.file_name
            # Скачиваем файл с Telegram
            downloaded_file = bot.download_file(file_info.file_path)

            # Загружаем файл на Google Диск
            upload_to_google_drive(downloaded_file, file_name, ff_id, service)
    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f"An error occurred: {error}")


def get_folder_name(message, nftn: Notification):
    return f"{message.chat.id} {nftn.notification_datetime.strftime('%d.%m.%Y %H:%M:%S')}"


def get_folder_id(message, nftn: Notification):
    folder_name = get_folder_name(message, nftn)
    creds = get_creds()
    try:
        service = build("drive", "v3", credentials=creds)
        results = service.files().list(
            q=f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'",
            spaces='drive',
            fields='files(id)'
        ).execute()
        items = results.get('files', [])
        if not items:
            print(f"Папка с названием '{folder_name}' не найдена.")
            return None
        return items[0]['id']
    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f"An error occurred: {error}")


def download_file(file_id):
    """Скачивает файл с Google Диска и возвращает его в виде байтовой строки."""
    creds = get_creds()
    try:
        service = build("drive", "v3", credentials=creds)

        request = service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        fh.seek(0)
        return fh.read()
    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f"An error occurred: {error}")


def get_notification_files(message, nftn: Notification):
    folder_id = get_folder_id(message, nftn)
    creds = get_creds()
    try:
        service = build("drive", "v3", credentials=creds)

        files = []
        page_token = None
        print("we are here")
        while True:
            response = service.files().list(
                q=f"'{folder_id}' in parents",
                spaces='drive',
                fields='nextPageToken, files(id, name)',
                pageToken=page_token
            ).execute()
            print("one time")

            files.extend(response.get('files', []))
            print(files)
            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break
        return files
    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f"An error occurred: {error}")


def update_files_on_disk(bot, message, nftn: Notification, docs):
    folder_id = get_folder_id(message, nftn)
    creds = get_creds()
    try:
        service = build("drive", "v3", credentials=creds)
        body_value = {'trashed': True}
        response = service.files().update(fileId=f"{folder_id}", body=body_value).execute()
        dt = nftn.notification_datetime.strftime('%d.%m.%Y %H:%M:%S')
        print(f"{message.chat.id} {dt}")
        file_metadata = {
            'name': f"{message.chat.id} {dt}",
            'mimeType': 'application/vnd.google-apps.folder',
        }
        file_folder = service.files().create(body=file_metadata, fields='id').execute()
        ff_id = file_folder.get("id")
        for doc in docs:
            # Получаем информацию о файле
            file_info = bot.get_file(doc.file_id)
            file_name = doc.file_name
            # Скачиваем файл с Telegram
            downloaded_file = bot.download_file(file_info.file_path)
            # Загружаем файл на Google Диск
            upload_to_google_drive(downloaded_file, file_name, ff_id, service)
        return True
    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f"An error occurred: {error}")


def offset_disk_folder(message, nftn: Notification):
    folder_id = get_folder_id(message, nftn)
    creds = get_creds()
    try:
        service = build("drive", "v3", credentials=creds)
        dt = nftn.notification_datetime + timedelta(days=nftn.day_interval)
        body_value = {
            "name": f"{message.chat.id} {dt.strftime('%d.%m.%Y %H:%M:%S')}"
        }
        response = service.files().update(fileId=f"{folder_id}", body=body_value).execute()
    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f"An error occurred: {error}")


def update_one_time_files_on_disk(bot, message, nftn: Notification, docs):
    offset_disk_folder(message, nftn)
    n_id = create_one_time_copy(nftn)[0]
    created = get_notification_by_id(n_id)
    creds = get_creds()
    try:
        service = build("drive", "v3", credentials=creds)
        dt = created.notification_datetime.strftime('%d.%m.%Y %H:%M:%S')
        print(f"{message.chat.id} {dt}")
        file_metadata = {
            'name': f"{message.chat.id} {dt}",
            'mimeType': 'application/vnd.google-apps.folder',
        }
        file_folder = service.files().create(body=file_metadata, fields='id').execute()
        ff_id = file_folder.get("id")
        for doc in docs:
            # Получаем информацию о файле
            file_info = bot.get_file(doc.file_id)
            file_name = doc.file_name
            # Скачиваем файл с Telegram
            downloaded_file = bot.download_file(file_info.file_path)
            # Загружаем файл на Google Диск
            upload_to_google_drive(downloaded_file, file_name, ff_id, service)
        offset_recurring_notification_by_interval(nftn)
        return True
    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f"An error occurred: {error}")


def store_db_entry(message, date, hour, minute, title):
    print(date)
    print(f"hour = {hour}, minute = {minute}")
    newdt = date.replace(hour=int(hour), minute=int(minute))
    stmt = (
        insert(Notification)
        .values(
            chat_id=message.chat.id,
            title=title,
            is_sent=False,
            is_recurring=False,
            notification_datetime=newdt
        )
    )
    with Session(engine) as session:
        res = session.execute(stmt)
        session.commit()


def get_awaited_notifications(message):
    stmt = (
        select(Notification)
        # select(Notification.id, Notification.title, Notification.is_recurring)
        .where(or_(
            Notification.is_recurring == True,
            Notification.is_sent == False
        ))
        .where(and_(Notification.chat_id == message.chat.id))
        .order_by(Notification.notification_datetime)
    )
    with Session(engine) as session:
        res = session.execute(stmt, execution_options={"prebuffer_rows": True})
    return res.scalars().all()


def get_sent_notifications(message):
    stmt = (
        select(Notification)
        .where(and_(
            Notification.is_sent == True,
            Notification.chat_id == message.chat.id
        ))
        .order_by(desc(Notification.notification_datetime))
    )
    with Session(engine) as sess:
        res = sess.execute(stmt, execution_options={"prebuffer_rows": True})
    return res.scalars().all()


def get_notification_by_id(n_id):
    stmt = (
        select(Notification)
        .where(Notification.id == n_id)
    )
    with Session(engine) as session:
        res = session.execute(stmt, execution_options={"prebuffer_rows": True})
    return res.scalars().first()


def change_title(n_id, title):
    stmt = (
        update(Notification)
        .where(Notification.id == n_id)
        .values(title=title)
    )
    with Session(engine) as session:
        res = session.execute(stmt)
        session.commit()


def create_one_time_copy(nftn: Notification, **kwargs):
    kwargs.setdefault("title", nftn.title)
    kwargs.setdefault("chat_id", nftn.chat_id)
    kwargs.setdefault("notification_datetime", nftn.notification_datetime)
    stmt = (
        insert(Notification)
        .values(kwargs)
    )
    with Session(engine) as sess:
        res = sess.execute(stmt)
        sess.commit()
    return res.inserted_primary_key


def offset_recurring_notification_by_interval(nftn: Notification):
    old_dt = nftn.notification_datetime
    new_dt = old_dt + timedelta(days=int(nftn.day_interval))
    stmt = (
        update(Notification)
        .where(Notification.id == nftn.id)
        .values(notification_datetime=new_dt)
    )
    print(str(stmt.compile(compile_kwargs={"literal_binds": True})))
    with Session(engine) as sess:
        res = sess.execute(stmt)
        sess.commit()


def copy_files_to_one_time_folder(message, created: Notification, files):
    creds = get_creds()
    try:
        service = build("drive", "v3", credentials=creds)
        dt = created.notification_datetime.strftime('%d.%m.%Y %H:%M:%S')
        print(f"{message.chat.id} {dt}")
        file_metadata = {
            'name': f"{message.chat.id} {dt}",
            'mimeType': 'application/vnd.google-apps.folder',
        }
        file_folder = service.files().create(body=file_metadata, fields='id').execute()
        ff_id = file_folder.get("id")
        for file in files:
            print(file['id'])
            body_value = {
                'name': file['name'],
                'parents': [ff_id]
            }
            service.files().copy(fileId=file['id'], body=body_value).execute()
    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f"An error occurred: {error}")


def change_one_time_title(message, nftn: Notification, title):
    new_id = create_one_time_copy(nftn, title=title)[0]
    print("new_id = ", new_id)
    created = get_notification_by_id(new_id)
    print("created new ntfn")
    files = get_notification_files(message, nftn)
    offset_disk_folder(message, nftn)
    copy_files_to_one_time_folder(message, created, files)
    offset_recurring_notification_by_interval(nftn)


def change_datetime(message, nftn: Notification, dt):
    creds = get_creds()
    folder_id = get_folder_id(message, nftn)
    try:
        service = build("drive", "v3", credentials=creds)
        body_value = {
            "name": f"{message.chat.id} {dt.strftime('%d.%m.%Y %H:%M:%S')}"
        }
        response = service.files().update(fileId=f"{folder_id}", body=body_value).execute()
    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f"An error occurred: {error}")
    n_id = nftn.id
    stmt = (
        update(Notification)
        .where(Notification.id == n_id)
        .values(notification_datetime=dt)
    )
    with Session(engine) as session:
        res = session.execute(stmt)
        session.commit()


def change_one_time_datetime(message, nftn: Notification, dt):
    new_id = create_one_time_copy(nftn, notification_datetime=dt)[0]
    created = get_notification_by_id(new_id)
    files = get_notification_files(message, nftn)
    copy_files_to_one_time_folder(message, created, files)
    # offset_disk_folder(message, nftn)
    # offset_recurring_notification_by_interval(nftn)


def delete_notification(message, nftn: Notification):
    n_id = nftn.id
    stmt = (
        delete(Notification)
        .where(Notification.id == n_id)
    )
    with Session(engine) as session:
        res = session.execute(stmt)
        session.commit()
    folder_id = get_folder_id(message, nftn)
    creds = get_creds()
    try:
        service = build("drive", "v3", credentials=creds)
        body_value = {'trashed': True}
        response = service.files().update(fileId=f"{folder_id}", body=body_value).execute()
    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f"An error occurred: {error}")


def change_interval(n_id, days):
    stmt = (
        update(Notification)
        .where(Notification.id == n_id)
        .values(day_interval=days)
    )
    with Session(engine) as sess:
        res = sess.execute(stmt)
        sess.commit()


def make_one_time(n_id):
    stmt = (
        update(Notification)
        .where(Notification.id == n_id)
        .values(is_recurring=False)
    )
    with Session(engine) as sess:
        res = sess.execute(stmt)
        sess.commit()


def make_recurring(n_id):
    stmt = (
        update(Notification)
        .where(Notification.id == n_id)
        .values(is_recurring=True)
    )
    with Session(engine) as sess:
        res = sess.execute(stmt)
        sess.commit()


def mark_as_sent(n_id):
    stmt = (
        update(Notification)
        .where(Notification.id == n_id)
        .values(is_sent=True)
    )
    # print(str(stmt.compile(compile_kwargs={"literal_binds": True})))
    with Session(engine) as sess:
        res = sess.execute(stmt)
        sess.commit()


def mark_as_awaited(n_id):
    stmt = (
        update(Notification)
        .where(Notification.id == n_id)
        .values(is_sent=False)
    )
    with Session(engine) as sess:
        res = sess.execute(stmt)
        sess.commit()


def show_notification(nftn: Notification):
    txt = nftn.title + f" {nftn.notification_datetime.strftime('%d.%m.%Y %H:%M')}"
    if nftn.is_recurring:
        txt = txt + f", recurring notification each {nftn.day_interval} days"
    else:
        txt = txt + ", one-time notification"
    return txt


def show_full_notification(nftn: Notification):
    txt = f"Title: {nftn.title}\n"
    txt = txt + f"Datetime: {nftn.notification_datetime.strftime('%d.%m.%Y %H:%M')}\n"
    if nftn.is_recurring:
        txt = txt + "Recurring notification\n"
    else:
        txt = txt + "One-time notification\n"
    return txt
