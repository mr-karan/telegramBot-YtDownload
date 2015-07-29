from __future__ import unicode_literals
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
sources_dict = {}
#URL=sys.argv[1]

#DONOT COMMIT API KEY. USE os.environ instead
API_URL="https://api.telegram.org/bot119926534:AAGiI4YRpRkA47wF-jkm5itLJUCS8FubGFg/"

def get_updates():
    log.debug('Checking for requests')
    return json.loads(requests.get(API_URL + 'getUpdates', params={'offset': last_updated+1}).text)


def my_hook(d):
    filename=d['filename'].split(".")[0]+".mp3"
    with open('song_name.txt', 'w') as f:
        f.write(str(filename))

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
    requests.post(API_URL+'sendMessage', data=payload)

def sendDocument(chat_id, filename):
    payload = {'chat_id': chat_id}
    file = {'document': open(filename,'rb')}
    requests.post(API_URL + "sendDocument", params=payload, files=file)

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
                urlGiven=chat_text
                downloadMp3(urlGiven)
                fileOpen=open('last_updated.txt', 'r')
                with open('song_name.txt','r') as f:
                    filename=f.read()
                sendDocument(chat_sender_id,filename)
                last_updated = req['update_id']
                fileOpen.close()
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
