#!/usr/bin/python
# -*- coding: utf-8 -*-
import socket,re,xchat

__module_name__ = "mpd-show-info"
__module_version__ = "0.2"
__module_description__ = "mpd show info"

host='127.0.0.1'
port=6600
init_string = ' ♫ '
end_string = ' ♫'
default_msg = "escuchando:"

custom_msg = default_msg

def mpd_sock_clean():
  global host, port
  mpd=socket.socket ( socket.AF_INET, socket.SOCK_STREAM )
  mpd.connect((host,port))
  file = mpd.makefile(mode='rw')
  welcome=mpd.recv(1024)
  return (mpd, file)

#begin inspired:
#convert info from mpd to dict format
#inspired in xchat_mpd from http://code.google.com/p/xchat-mpd/
def checkAnswer(answer, ok_mess=None, ack_mess=None, add_answer=True):
	if not answer:
		xchat.prnt('MPD connection reset by peer')
	elif answer[:2] == 'OK':
		if ok_mess != None: xchat.prnt(ok_mess + (answer if add_answer else ''))
	else:
		if ack_mess != None: xchat.prnt(ack_mess + (answer if add_answer else ''))
	return answer

get_dict_format = re.compile(r'^(?P<key>[^:]+):\s*(?P<value>.*)$')

# mpd_get_command
# params:
#  mpdsock: socket of mpd
#  data: file for read in dict format
#  command: command to pass to mpd cli
# return: 
#  dict formatted data
def mpd_get_command(mpdsock, data, command):
  keydict = {}
  mpdsock.send(command+'\r\n')
  while True:
    line = data.readline()
    if checkAnswer(line):
      m = get_dict_format.match(line[:-1])
      if m:
	keydict[m.group('key')] = m.group('value')
      else:
	checkAnswer(line, ack_mess = '')
	break
    else:
      break
  return keydict

#end inspired:

# todo: convert def to command list element
def mpd_current_song(data):
  artist=data.get('Artist', None)
  title=data.get('Title', None)
  album=data.get('Album', None)
  #not info from track
  if not artist:
    filename=data.get('file', None)
    if filename:
      filename=filename[filename.rindex("/")+1:].split('.')[0]
    msg= filename 
  else:
    msg= artist+' -' + title + ' -' + album
  return msg

# def command list
# 
# params: 
#   mpdsock: sock for connect to mpd
#   filedata: file for use to read data in dict format
# return:
#   msg: string of msg to display

# mpd_file: read filename data
def mpd_file(mpdsock, filedata):
  data=mpd_get_command(mpdsock,filedata,"currentsong")
  filename=data.get('file',None)
  if filename:
    filename=filename[filename.rindex("/")+1:]
  return filename

# add new commands
# 'name_of_command': command_to_apply
command_to_def = {
	'file': mpd_file,
}


def playing(word, word_eol, userdata):
  global custom_msg, init_string, end_string, default_msg
  mpd, filedata =mpd_sock_clean()
  if len(word) < 2:
    custom_msg=default_msg
    msg=mpd_current_song( mpd_get_command(mpd, filedata,"currentsong"))
  else:
    calldef = command_to_def.get(word[1], None)
    if calldef:
      if len(word) < 3:
	custom_msg=default_msg
      else:
	custom_msg=word_eol[2]+":"
      msg = apply(calldef, (mpd,filedata,))
    else:
      custom_msg=word_eol[1]+":"
      msg=mpd_current_song( mpd_get_command(mpd, filedata,"currentsong"))
      
  # format message
  msg=custom_msg + init_string + msg + end_string
  xchat.command('me ' + msg)
  data=""
  mpd.close()
  return xchat.EAT_ALL
  #hooks into the show xchat command
xchat.hook_command("mpd",playing, help="/mpd [custom message]")
