#!/bin/bash

if [ $1 == -h ]
    then
	echo "Usage: ./schedule.sh HOUR MINUTE"
	exit
fi

mkdir $HOME/.mirror0 2>/dev/null; cp ./mirror0.in_ $HOME/.mirror0/mirror0.ini 

crontab -r 2>/dev/null
echo "$2 $1 * * * cd $(pwd); python mirror0.py afl > $HOME/.mirror0/current_afl.log 2>&1; python mirror0.py yahoo > $HOME/.mirror0/current_yahoo.log 2>&1" | crontab -
