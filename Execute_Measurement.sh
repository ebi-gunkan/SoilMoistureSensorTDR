#!/bin/sh

NOW_M_BEFORE=-1

sudo chmod 666 /dev/ttyACM0

while true;do
  NOW_M=`date '+%H'`

  sudo chmod 666 /dev/ttyACM0

  if [ $NOW_M -ne $NOW_M_BEFORE ]; then
    echo "begin measurement:" `date`

    #point:101
    ANS="1"
    while [ $ANS = "1" ]; do
      echo "measuring..."
      ANS=$(python3 ./main.py;)
      sleep 10
      sudo chmod 666 /dev/ttyACM0
      sleep 1
    done

    NOW_M_BEFORE=$NOW_M
    echo "finish:" `date`
  fi
  sleep 1
done
