#!/bin/bash
if [ "$#" -ne 5 ]
then
 echo "Usage $0 <dase_dir> <file_type> <profile> <domain> <days>"
exit
fi

if [[ $2 == "callrecording" ]]
then
 /usr/bin/find ${1}/recordings/${4}/archive/*  -name '*.wav' -mtime +${5} -exec rm {} \;
 /usr/bin/find ${1}/recordings/${4}/archive/*  -name '*.mp3' -mtime +${5} -exec rm {} \;
fi

if [[ $2 == "voicemailmsg" ]]
then
 vmdbfile="/var/lib/freeswitch/vm_db/voicemail_${3}.db"
 /usr/bin/find ${1}/voicemail/${3}/${4}/*  -name 'msg_*.wav' -mtime +${5} -exec rm {} \;
 /usr/bin/find ${1}/voicemail/${3}/${4}/*  -name 'msg_*.mp3' -mtime +${5} -exec rm {} \;
 if [ -f "$vmdbfile" ]
 then
  secs=$(( $5 * 86400 ))
  now_epoch=$(/usr/bin/date +%s)
  secs=$(( $now_epoch - $secs ))
  /usr/bin/sqlite3 ${vmdbfile} "delete from voicemail_msgs where created_epoch < $secs;"
 fi
fi
