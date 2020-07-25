#!/bin/bash

# parameter
T="$1"
I="$2"
D="--disable-server"

# xdo

read DW DH < <(xdotool getdisplaygeometry)

TW=$(($DW*2/3))  # desired terminal width
TH=$(($DH*2/3))  # desired terminal hight
TX=$((($DW-$TW)/2))
TY=$((($DH-$TH)/2))

XSIZE="xdotool getactivewindow windowsize $TW $TH"
XMOVE="xdotool getactivewindow windowmove $TX $TY"
XDO="$XSIZE; $XMOVE"

CW=10 # char width - rough default
CH=20 # char hight - rough default

G="--geometry=$(($TW/$CW))x$(($TH/$CH))+$TX+$TY"

C='bash -c "sleep 1; '$XDO'; '$3'"'
K='bash -c "sleep 1; '$3'"'

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
        if pgrep -x plasmashell >/dev/null; then
           konsole --nofork --hide-menubar -qwindowgeometry "${TW}x${TH}+$TX+$TY" -qwindowicon "mx-updater" -qwindowtitle "$T" -e "$K" 
        else
           konsole -e "$C" 
           sleep 5
        fi
        ;;
  *roxterm) 
        roxterm "$G" -T "$T" --separate -e "$C" 
        ;;
  *xfce4-terminal.wrapper | *xfce4-terminal) 
        xfce4-terminal --hide-menubar $D $G  --icon="$I"  -T "$T" -e "$C"
        ;;
  *xterm) 
        xterm  -fa monaco -fs 12 -bg black -fg white  -xrm 'XTerm.vt100.allowTitleOps: false' -T "$T"  -e "$C" 
        ;;
  *) x-terminal-emulator -T "$T" -e "$C" 
        ;;
esac

exit
