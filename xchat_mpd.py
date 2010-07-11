#!/usr/bin/python
# -*- coding: utf-8 -*-
import socket,re,xchat

__module_name__ = "mpd-np"
__module_version__ = "0.1"
__module_description__ = "mpd now playing"

host='127.0.0.1'
port=6600
init_string = ' ♫'
end_string = ' ♫'

def playing(word, word_eol, userdata):
  if len(word) < 2:
    custom_msg="escuchando:"
  else:
    custom_msg=word_eol[1]+":"
  mpd=socket.socket ( socket.AF_INET, socket.SOCK_STREAM )
  mpd.connect((host,port))
  mpd.send('currentsong\r\n')
  #get all the info about current track being played
  data=mpd.recv(4096)
  try:
    artist=re.findall(r'Artist[:]\s[\S ]+',data)[0].split(':')[1]
  except:
    artist=""
  try:
    title=re.findall(r'Title[:]\s[\S ]+',data)[0].split(':')[1]
  except:
    title=""
  try:
    album=re.findall(r'Album[:]\s[\S]+',data)[0].split(':')[1]
  except:
    album=""
  if artist == "":
    try:
      filename=re.findall(r'file[:]\s[\S ]+',data)[0].split(':')[1]
      filenamesplit=filename[filename.rindex("/")+1:].split(".")
    except:
      filenamesplit[0]="some song"
    msg=custom_msg + init_string + filenamesplit[0] + end_string
  else
    msg=custom_msg + init_string + artist+' -' + title + ' -' + album + end_string
  xchat.command('me ' + msg)
  data=""
  mpd.close()
  return xchat.EAT_ALL
  #hooks into the show xchat command
xchat.hook_command("mpd",playing, help="/mpd [custom message]")
