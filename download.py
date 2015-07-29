from __future__ import unicode_literals
import youtube_dl
import sys
import os
import requests
import logging
import re
import json

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('musicBot')
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
API_URL=os.environ['TELEGRAM_BOT']

def get_updates():
    log.debug('Checking for requests')
    return json.loads(requests.get(API_URL + 'getUpdates', params={'offset': last_updated+1}).text)


def my_hook(d):
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')


#download and strip to mp3

#download and strip to mp3
def getfilename(urlGiven):
    ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'logger': MyLogger(),
    'progress_hooks': [my_hook],
}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download(['http://www.youtube.com/watch?v=BaW_jenozKc'])

    '''p=subprocess.check_output(["youtube-dl",urlGiven, "--youtube-skip-dash-manifest","--extract-audio","--audio-format","mp3","--audio-quality","0" ,"-o","'%(title)s-%(id)s.%(ext)s'","--restrict-filenames","--get-filename"]).decode("utf-8").strip("\n")
    ext=p.split(".")
    ext[1]="mp3"
    filename=ext[0]+"."+ext[1]
    return filename
    '''



def downloadMp3(urlGiven):
    p=subprocess.check_output(["youtube-dl",urlGiven, "--youtube-skip-dash-manifest","--extract-audio","--audio-format","mp3","--audio-quality","0" ,"-o","'%(title)s-%(id)s.%(ext)s'","--restrict-filenames","--download"])
    return p

def sendMessage(chat_id, text):
    payload = {'chat_id': chat_id, 'text': text}
    requests.post(API_URL+'sendMessage', data=payload)

def sendDocument(chat_id, filename):
    payload = {'chat_id': chat_id}
    file = {'document': open(filename,'rb')}
    requests.post(API_URL + "sendDocument", params=payload, files=file)



def sendMessage(chat_id, text):
    payload = {'chat_id': chat_id, 'text': text}
    requests.post(API_URL+'sendMessage', data=payload)

def sendDocument(chat_id, file):
    payload = {'chat_id': chat_id}
    songfile=open('song_title.txt', 'r')
    fileName=songfile.read().splitlines()
    nameoffile=fileName[0]+'.mp3'
    file = {'document': open(nameoffile,'rb')}
    requests.post(API_URL + "sendDocument", params=payload, files=file)

#downloadMp3()
if __name__ == '__main__':
    log.debug('Last updated id: {0}'.format(last_updated))
    while (True):
        r = get_updates()
        if r['ok']:
            for req in r['result']:
                chat_sender_id = req['message']['chat']['id']
                chat_text = req['message']['text']
                urlGiven=chat_text
                linksend=downloadMp3(urlGiven)
                #sendMessage(chat_sender_id,len(chat_text))
                sendMessage(chat_sender_id,linksend)
                last_updated = req['update_id']
                if chat_text == '/stop':
                    log.debug('Added {0} to skip list'.format(chat_sender_id))
                    skip_list.append(chat_sender_id)
                    last_updated = req['update_id']
                    sendMessage(chat_sender_id, "Bot Has been stopped. Use /start again to download ")

                if chat_text == '/start':
                    helptext = '''
                        Hi! This is Music Downloader Bot.
                    '''
                    sendMessage(chat_sender_id, helptext)
                    last_updated = req['update_id']

                with open('last_updated.txt', 'w') as f:
                    f.write(str(last_updated))
                    log.debug(
                        'Updated last_updated to {0}'.format(last_updated))
                f.close()
