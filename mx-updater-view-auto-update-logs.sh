#!/bin/bash

# parameter
T="$1"
I="$2"
D="--disable-server"

# xdo

read DW DH < <(xdotool getdisplaygeometry)

TW=$(($DW*2/3))  # desired terminal width
TH=$(($DH*2/3))  # desired terminal hight

XSIZE="xdotool getactivewindow windowsize $TW $TH"
XMOVE="xdotool getactivewindow windowmove $((($DW-$TW)/2)) $((($DH-$TH)/2))"
XDO="$XSIZE; $XMOVE"

CW=10 # char width - rough default
CH=20 # char hight - rough default

G="--geometry=$(($TW/$CW))x$(($TH/$CH))+$((($DW-$TW)/2))+$((($DH-$TH)/2))"

C='bash -c "sleep 1; '$XDO'; mx-updater_unattended_upgrades_log_view"'

# default to /usr/bin/xfce4-terminal

XT=/usr/bin/x-terminal-emulator
if [ -x /usr/bin/xfce4-terminal ];  then
     XT=/usr/bin/xfce4-terminal
fi


case $(readlink -e $XT) in
  
  *gnome-terminal.wrapper) 
        gnome-terminal.wrapper $G -T "$T" -e "$C"
        ;;
  *konsole) 
        konsole -e "$C" 
        sleep 5
        ;;
  *roxterm) 
        roxterm "$G" -T "$T" --separate -e "$C" 
        ;;
  *xfce4-terminal.wrapper | *xfce4-terminal) 
        xfce4-terminal $D $G  --icon="$I"  -T "$T" -e "$C"
        ;;
  *xterm) 
        xterm  -fa monaco -fs 12 -bg black -fg white  -xrm 'XTerm.vt100.allowTitleOps: false' -T "$T"  -e "$C" 
        ;;
  *) x-terminal-emulator -T "$T" -e "$C" 
        ;;
esac

exit

