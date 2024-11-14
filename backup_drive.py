import os
import re
import zipfile
from google.oauth2 import service_account
from googleapiclient.discovery import build
import subprocess
import datetime
import shutil
import io
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from utils import get_creds, download_file


BACKUP_DIR = 'BACKUP_DIR'
DB_HOST = 'localhost'
DB_NAME = 'RpiLab'
DB_USER = 'postgres'
DB_PASSWORD = '28Jun2003'
BACKUP_FOLDER_ID = '1j5prGFSN5L7T1PQuYuOslzlbJFxf17o9'


def get_service():
  creds = get_creds()
  return build('drive', 'v3', credentials=creds)


def check_format(input_string):
    # Define the regex pattern
    pattern = r'^\d+\s\d{2}\.\d{2}\.\d{4}\s\d{2}:\d{2}:\d{2}$'
    print(f"Checking {input_string}")
    
    # Use fullmatch to check if the whole string matches the pattern
    if re.fullmatch(pattern, input_string):
        return True
    else:
        return False


def backup_folder_id():
  service = get_service()
  folder_name = 'backup'
  results = service.files().list(
      q=f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'",
      spaces='drive',
      fields='files(id)'
  ).execute()
  items = results.get('files', [])
  if not items:
      print(f"Folder '{folder_name}' not found.")
      return None
  return items[0]['id']


def download_files_from_drive(output_dir):
  creds = get_creds()
  service = build('drive', 'v3', credentials=creds)
  response = service.files().list().execute()
  items = response.get('files', [])
  
  if not items:
    print("Nothing was downloaded")
    return
  for item in items:
    file_id = item['id']
    file_name = item['name']
    print(f"Download file {file_name} id={file_id}")
    
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    
    while not done:
      done, _ = downloader.next_chunk()
    
    with open(os.path.join(output_dir, file_name, 'wb')) as f:
      f.write(fh.getbuffer())
    
    print(f"File {file_name} if={file_id} successfully downloaded")


def download_files_rec(service, folder_id, local_folder):
    query = f"'{folder_id}' in parents"
    results = service.files().list(q=query, fields="files(id, name, mimeType)").execute()
    items = results.get('files', [])

    for item in items:
        file_path = os.path.join(local_folder, item['name'])
        file_path = file_path.replace(':', '_')
        if item['mimeType'] == 'application/vnd.google-apps.folder':  # If it's a directory
          
            os.makedirs(file_path, exist_ok=True)
            download_files_rec(service, item['id'], file_path)  # Recursion
        else:  # It's a file
            print(f'Downloading {item["name"]}...')
            request = service.files().get_media(fileId=item['id'])
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
            with open(file_path, 'wb') as f:
                f.write(fh.getbuffer())
            print(f'File {item["name"]} downloaded successfully.')


def download_files_correctly(output_dir):
  service = get_service()
  query = "'me' in owners"
  response = service.files().list(q=query).execute()
  # top level, downloading all the folders or files by themselves and checking that they are indeed folders
  items = response.get('files', [])
  for item in items:
    item_id = item['id']
    item_name = item['name']
    item_type = item['mimeType']
    if item_type == 'application/vnd.google-apps.folder' and check_format(item_name):
      print(f"{item_name} {item_id} is a directory, now we download its files")
      file_path = os.path.join(output_dir, item_name)
      file_path = file_path.replace(':', '_')
      os.makedirs(file_path, exist_ok=True)
      download_files_rec(service, item_id, file_path)


def create_db_dump():
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    dump_file = f"{BACKUP_DIR}/db_dump_{timestamp}.sql"
    os.environ['PGPASSWORD'] = '28Jun2003'
    os.system(f'pg_dump -h {DB_HOST} -U {DB_USER} -d {DB_NAME} -f {dump_file}')
    return dump_file


def archive_files(local_folder):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    archive_name = f"archive_{timestamp}.zip"
    with zipfile.ZipFile(archive_name, 'w') as zipf:
        for root, dirs, files in os.walk(local_folder):
            for file in files:
                zipf.write(os.path.join(root, file),
                    os.path.relpath(os.path.join(root, file), 
                    os.path.join(local_folder, '..')))
    return archive_name


def upload_archive(service, local_file):
    file_metadata = {
      'name': os.path.basename(local_file),
      'parents': [BACKUP_FOLDER_ID]
    }
    media = MediaFileUpload(local_file, mimetype='application/zip', resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print(f'Uploaded {local_file} with ID {file.get("id")}')


if not os.path.exists(BACKUP_DIR):
  os.makedirs(BACKUP_DIR)


download_files_correctly(BACKUP_DIR)
create_db_dump()

archive_name = archive_files(BACKUP_DIR)
upload_archive(get_service(), archive_name)


# print(backup_folder_id())
