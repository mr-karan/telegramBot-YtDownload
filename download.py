from __future__ import unicode_literals
from urllib.parse import urlparse,urlsplit

import youtube_dl
import sys
import os
import requests
import logging
import re
import subprocess
import json

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('nbt')
try:
    with open('last_updated.txt', 'r') as f:
        try:
            last_updated = int(f.read())
        except ValueError:
            last_updated = 0
    f.close()
except FileNotFoundError:
    last_updated = 0

skip_list = []

#URL=sys.argv[1]

#DONOT COMMIT API KEY. USE os.environ instead

BOT_KEY = os.environ['YTBOT_ACCESS_TOKEN']
API_BASE = 'https://api.telegram.org/bot'
def validurl(url):
    try:
        valid=requests.get(url)
        return valid.url
    except requests.exceptions.MissingSchema:
        print("Not valid url")

def get_updates():
    log.debug('Checking for requests')
    return json.loads(requests.get(API_BASE + BOT_KEY + '/getUpdates', params={'offset': last_updated+1}).text)


def my_hook(d):
    #if d['status']=='downloading':
        #sendMessage(chat_sender_id,"Wait for a few moments, please")
        #last_updated = req['update_id']

    filename, file_extension = os.path.splitext(d['filename'])
    file_extension='.mp3'
    finalname=filename+file_extension
    with open('song_name.txt', 'w') as f:
        f.write(str(finalname))

def downloadMp3(urlGiven):
    ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'progress_hooks': [my_hook],
}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([urlGiven])

def sendMessage(chat_id, text):
    payload = {'chat_id': chat_id, 'text': text}
    requests.post(API_BASE + BOT_KEY+'/sendMessage', data=payload)

def sendDocument(chat_id, filename):
    payload = {'chat_id': chat_id}
    file = {'document': open(filename,'rb')}
    requests.post(API_BASE + BOT_KEY + "/sendDocument", params=payload, files=file)

#downloadMp3()
if __name__ == '__main__':
    log.debug('Starting up')
    log.debug('Last updated id: {0}'.format(last_updated))
    while (True):
        r = get_updates()
        if r['ok']:
            for req in r['result']:
                chat_sender_id = req['message']['chat']['id']
                chat_text = req['message']['text']
                log.debug('Chat text received: {0}'.format(chat_text))
                urlGiven=validurl(chat_text)
                #fileOpen=open('last_updated.txt', 'r')
                try:
                    downloadMp3(urlGiven)
                except youtube_dl.utils.DownloadError:
                    sendMessage(chat_sender_id,"Please enter correct youtube.com URL only.Mobile links not supported as of now ")
                    last_updated = req['update_id']

                with open('song_name.txt','r') as f:
                    filename=f.read()
                    sendDocument(chat_sender_id,filename)



                last_updated = req['update_id']

                #fileOpen.close()
                if chat_text == '/stop':
                    log.debug('Added {0} to skip list'.format(chat_sender_id))
                    skip_list.append(chat_sender_id)
                    last_updated = req['update_id']
                    sendMessage(chat_sender_id, "Ok, we won't send you any more messages.")

                if chat_text == '/start':
                    helptext = '''
                        Hi! This is Music Downloader Bot
                    '''
                    sendMessage(chat_sender_id, helptext)
                    last_updated = req['update_id']

                with open('last_updated.txt', 'w') as f:
                    f.write(str(last_updated))
                    log.debug(
                        'Updated last_updated to {0}'.format(last_updated))
                f.close()
