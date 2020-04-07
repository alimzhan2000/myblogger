from __future__ import print_function
from apiclient.http import MediaFileUpload, MediaIoBaseDownload
import os, io
import logging  
from apiclient import discovery 
from httplib2 import Http  
from oauth2client import file, client, tools 
from oauth2client.file import Storage 
from googleapiclient.discovery import build

import config
import telebot
from telebot.types import InputMediaPhoto, InputMediaVideo
from telebot import types

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)  
logger = logging.getLogger(__name__)  

SCOPES = 'https://www.googleapis.com/auth/drive'
store = file.Storage('storage.json')  
creds = store.get()  
if not creds or creds.invalid:  
    flow = client.flow_from_clientsecrets('client_secrets.json', SCOPES)  
    creds = tools.run_flow(flow, store)  
drive_service = discovery.build('drive', 'v3', http=creds.authorize(Http()),cache_discovery=False) 

def download_photo(file_id):
    request = drive_service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print ("Download %d%%." % int(status.progress() * 100))
    return fh.getvalue()

def document_handler(message, bot):
    folder_id = '1XjIl-IBxYh0frbvxg9HyHsN1ppyNf-nZ'
    file_id = message.photo[0].file_id
    file = bot.get_file(file_id)
    downloaded_file = bot.download_file(file.file_path)
    with open(file_id, 'wb') as new_file:
        new_file.write(downloaded_file)

    file_metadata = {
    'name': [file_id],
    'parents': [folder_id]
    }
    media = MediaFileUpload(file_id, mimetype='image/jpeg', resumable=True)
    file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    return file.get('id')