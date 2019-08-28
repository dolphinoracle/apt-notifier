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


G="--geometry=$(($DW/100*67/10))x$(($DH/100*67/20))+$((($DW - $DW/100*67)/2))+$((($DH - $DH/100*67)/2))"

C='bash -c mx-updater_unattended_upgrades_dpkg_log_view'
# 
# for test


#T="${1#*--title=}"
#I="${2#*--icon=}"

case $(readlink -e /usr/bin/x-terminal-emulator) in
  
  *gnome-terminal.wrapper) gnome-terminal.wrapper $G -T "$T" -e "$C" & redraw-terminal
                          ;;
                 *konsole) konsole -e "$C"  & redraw-terminal
                          sleep 5
                          ;;
                 *roxterm) roxterm "$G" -T "$T" --separate -e "$C"  & redraw-terminal
                          ;;
  *xfce4-terminal.wrapper) xfce4-terminal $G  --icon="$2"  --title="$1" -e "$C" 2>/dev/null & redraw-terminal
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

