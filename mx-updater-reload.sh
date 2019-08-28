#!/bin/bash
#set -x

##############

read DW DH < <(xdotool getdisplaygeometry)

redraw-terminal() {
  
  sleep 1
# read DW DH < <(xdotool getdisplaygeometry)

  xdotool getactivewindow windowsize $(($DW/100*67)) $(($DH/100*67))

  xdotool getactivewindow windowmove $((($DW - $DW/100*67)/2))  $((($DH - $DH/100*67)/2))
}


P="${3}"
G="--geometry=$(($DW/100*67/10))x$(($DH/100*67/20))+$((($DW - $DW/100*67)/2))+$((($DH - $DH/100*67)/2))"

C='bash -c "echo apt-get update; sleep 1; apt-get update; sleep 1; echo; read -n1 -sr -p'"'$P'"';"'
# 
# for test


T="${1#*--title=}"
I="${2#*--icon=}"

: ${T:=MX-Updater: Reload}
: ${I:=mnotify-some-classic}


case $(readlink -e /usr/bin/x-terminal-emulator) in
  
  *gnome-terminal.wrapper) gnome-terminal.wrapper $G -T "$T" -e "$C" & redraw-terminal
                          ;;
                 *konsole) konsole -e "$C"  & redraw-terminal
                          sleep 5
                          ;;
                 *roxterm) roxterm "$G" -T "$T" --separate -e "$C"  & redraw-terminal
                          ;;
  *xfce4-terminal.wrapper) xfce4-terminal $G  --icon="$I"  -T "$T" -e "$C" & redraw-terminal
                          ;;
                   *xterm) if [ -e /usr/bin/xfce4-terminal ]
                            then
                              xfce4-terminal $G --icon="$I" -T "$T" -e "$C" & redraw-terminal
                            else
							  xterm -xrm 'XTerm.vt100.allowTitleOps: false' -T "$T"  -e "$C"  & redraw-terminal
                          fi
                          ;;
                       *) x-terminal-emulator -T "$T" -e "$C"  & redraw-terminal
                          ;;
esac

exit


# 80x25
# xfce4-terminal --geometry=80x25+$((($DW - 800)/2))+$((($DH - 500)/2))  -e 'bash -c "echo apt-get update;sleep 1; read -p ReadMe me"' & redraw-terminal
