#!/usr/bin/python
# -*- coding: utf-8 -*-
import subprocess
import sys
import os
import tempfile
from os import environ

from PyQt4 import QtGui
from PyQt4 import QtCore

rc_file_name = environ.get('HOME') + '/.config/apt-notifierrc'
message_status = "not displayed"

# ~~~ Localize 0 ~~~

# Use gettext and specify translation file locations
import gettext
gettext.bindtextdomain('apt-notifier', '/usr/share/locale')
gettext.textdomain('apt-notifier')
_ = gettext.gettext
gettext.install('apt-notifier.py')

from string import Template	# for simple string substitution (popup_msg...)

def set_translations():
    global tooltip_0_updates_available
    global tooltip_1_new_update_available
    global tooltip_multiple_new_updates_available
    global popup_title
    global popup_msg_1_new_update_available
    global popup_msg_multiple_new_updates_available
    global Upgrade_using_Synaptic
    global View_and_Upgrade
    global Hide_until_updates_available
    global Quit_Apt_Notifier
    global Apt_Notifier_Help
    global Synaptic_Help
    global Apt_Notifier_Preferences    
    global Apt_History
    global Check_for_Updates
    global Check_for_Updates_by_User
    Check_for_Updates_by_User = 'false'
    global ignoreClick
    ignoreClick = '0'
    global RepoListsHashNow
    RepoListsHashNow = ''
    global RepoListsHashPrevious
    RepoListsHashPrevious= ''
    global AptConfsAndPrefsNow
    AptConfsAndPrefsNow = ''
    global AptConfsAndPrefsPrevious
    AptConfsAndPrefsPrevious = ''
    global AptPkgCacheHashNow
    AptPkgCacheHashNow = ''
    global AptPkgCacheHashPrevious
    AptPkgCacheHashPrevious = ''
    global text
    text = ''

    # ~~~ Localize 1 ~~~

    tooltip_0_updates_available                 = unicode (_("0 updates available")                    ,'utf-8')
    tooltip_1_new_update_available              = unicode (_("1 new update available")                 ,'utf-8')
    tooltip_multiple_new_updates_available      = unicode (_("$count new updates available")           ,'utf-8')
    popup_title                                 = unicode (_("Updates")                                ,'utf-8')
    popup_msg_1_new_update_available            = unicode (_("You have 1 new update available")        ,'utf-8')
    popup_msg_multiple_new_updates_available    = unicode (_("You have $count new updates available")  ,'utf-8')
    Upgrade_using_Synaptic                      = unicode (_("Upgrade using Synaptic")                 ,'utf-8')
    View_and_Upgrade                            = unicode (_("View and Upgrade")                       ,'utf-8')         
    Hide_until_updates_available                = unicode (_("Hide until updates available")           ,'utf-8')
    Quit_Apt_Notifier                           = unicode (_("Quit")                                   ,'utf-8')
    Apt_Notifier_Help                           = unicode (_("Apt-Notifier Help")                      ,'utf-8')
    Synaptic_Help                               = unicode (_("Synaptic Help")                          ,'utf-8')
    Apt_Notifier_Preferences                    = unicode (_("Preferences")                            ,'utf-8')
    Apt_History                                 = unicode (_("Apt History")                            ,'utf-8')
    Check_for_Updates                           = unicode (_("Check for Updates")                      ,'utf-8')
  
# Check for updates, using subprocess.Popen
def check_updates():
    global message_status
    global text
    global RepoListsHashNow
    global RepoListsHashPrevious
    global AptConfsAndPrefsNow
    global AptConfsAndPrefsPrevious
    global AptPkgCacheHashNow
    global AptPkgCacheHashPrevious
    global Check_for_Updates_by_User
    
    """
    Don't bother checking for updates when /var/lib/apt/periodic/update-stamp
    isn't present. This should only happen in a Live session before the repository
    lists have been loaded for the first time.
    """ 
    command_string = "[ ! -e /var/lib/apt/periodic/update-stamp ]"
    exit_state = subprocess.call([command_string], shell=True, stdout=subprocess.PIPE)
    if exit_state == 0:
        if text == '':
            text = '0'
        message_status = "not displayed"  # Resets flag once there are no more updates
        add_hide_action()
        if icon_config != "show":
            AptIcon.hide()
        else:
            AptIcon.setIcon(NoUpdatesIcon)
            AptIcon.setToolTip(tooltip_0_updates_available)
        return
    
    """
    Don't bother checking for updates if processes for other package management tools
    appear to be runninng.
    """ 
    command_string = "ps aux | grep -v grep | grep -E 'apt-get|aptitude|dpkg|gdebi|synaptic' -q"
    exit_state = subprocess.call([command_string], shell=True, stdout=subprocess.PIPE)
    if exit_state == 0:
        return
    
    """
    Get a hash of the /var/lib/apt/lists folder.
    """
    script = '''#!/bin/sh
    find /var/lib/apt/lists/* 2>/dev/null | xargs md5sum 2>/dev/null | md5sum
    '''
    script_file = tempfile.NamedTemporaryFile('wt')
    script_file.write(script)
    script_file.flush()
    run = subprocess.Popen(["echo -n `bash %s`" % script_file.name],shell=True, stdout=subprocess.PIPE)
    RepoListsHashNow = run.stdout.read(128)
    script_file.close()

    """
    Get a hash of the /etc/apt/conf file and files in the .d folder,
    and /etc/apt/preferences file and files in the .d folder.
    """    
    script = '''#!/bin/sh
    find /etc/apt/{apt.conf*,preferences*} 2>/dev/null | grep -v .d$ | xargs md5sum  2>/dev/null | md5sum
    '''
    script_file = tempfile.NamedTemporaryFile('wt')
    script_file.write(script)
    script_file.flush()
    run = subprocess.Popen(["echo -n `bash %s`" % script_file.name],shell=True, stdout=subprocess.PIPE)
    AptConfsAndPrefsNow = run.stdout.read(128)
    script_file.close()
    
    """
    Get a hash of /var/cache/apt/pkgcache.bin.
    """    
    script = '''#!/bin/sh
    md5sum  /var/cache/apt/pkgcache.bin 2>/dev/null | md5sum
    '''
    script_file = tempfile.NamedTemporaryFile('wt')
    script_file.write(script)
    script_file.flush()
    run = subprocess.Popen(["echo -n `bash %s`" % script_file.name],shell=True, stdout=subprocess.PIPE)
    AptPkgCacheHashNow = run.stdout.read(128)
    script_file.close()

    """
    If
        no changes in the Repo List hashes since last checked
            AND 
        the Apt Conf & Apt Preferences hashes same since last checked
            AND
        pkgcache.bin same since last checked
            AND
        the call to check_updates wasn't initiated by user   
    then don't bother checking for updates.
    """
    if RepoListsHashNow == RepoListsHashPrevious:
        if AptConfsAndPrefsNow == AptConfsAndPrefsPrevious:
            if AptPkgCacheHashNow == AptPkgCacheHashPrevious:
                if Check_for_Updates_by_User == 'false':
                    if text == '':
                        text = '0'
                    return

    RepoListsHashPrevious = RepoListsHashNow
    RepoListsHashNow = ''

    AptConfsAndPrefsPrevious = AptConfsAndPrefsNow
    AptConfsAndPrefsNow = ''
    
    AptPkgCacheHashPrevious = AptPkgCacheHashNow
    AptPkgCacheHashNow = ''
    
    Check_for_Updates_by_User = 'false'
    
    #Create an inline script (what used to be /usr/bin/apt-notifier-check-Updates) and then run it to get the number of updates.
    script = '''#!/bin/sh
    sorted_list_of_upgrades() 
    {
        #Create a sorted list of the names of the packages that are upgradeable.
        LC_ALL=en_US apt-get -o 'Debug::NoLocking=true' --trivial-only -V $(grep ^UpgradeType ~/.config/apt-notifierrc | cut -f2 -d=) 2>/dev/null \\
        |  sed -n '/upgraded:/,$p' | grep ^'  ' | awk '{ print $1 }' | sort
    }
    
    #suppress updates available indication if 2 or more Release.reverify entries found
    #if [ $(ls -1 /var/lib/apt/lists/partial/ | grep Release.reverify$ | wc -l) -ge 2 ]; then echo 0; exit; fi 
    
    if [ -s /var/lib/synaptic/preferences ]; 
        then 
            #/var/lib/synaptic/preferences is a non-zero size file, which means there are packages pinned in Synaptic. 
            #Remove from the sorted_list_of_upgrades, packages that are pinned in Synaptic, and then get a count of remaining.
            
            sorted_list_of_upgrades | grep -vx $(grep 'Package:' /var/lib/synaptic/preferences 2>/dev/null | awk {'print "-e " $2'}) | wc -l
        
        else 
            #/var/lib/synaptic/preferences is either a zero byte file, meaning packages were pinned in Synaptic at some time in 
            # the past but none are currently pinned. Or the file is not present, meaning packages have never been pinned using 
            # Synaptic. In either case, just get a count of how many upgradeable packages are in the list.
            
            sorted_list_of_upgrades | wc -l
    fi
    '''
    script_file = tempfile.NamedTemporaryFile('wt')
    script_file.write(script)
    script_file.flush()
    run = subprocess.Popen(["echo -n `sh %s`" % script_file.name],shell=True, stdout=subprocess.PIPE)
    # Read the output into a text string
    text = run.stdout.read(128)
    script_file.close()

    # Alter both Icon and Tooltip, depending on updates available or not 
    if text == "0":
        message_status = "not displayed"  # Resets flag once there are no more updates
        add_hide_action()
        if icon_config != "show":
            AptIcon.hide()
        else:
            AptIcon.setIcon(NoUpdatesIcon)
            AptIcon.setToolTip(tooltip_0_updates_available)
    else:
        if text == "1":
            AptIcon.setIcon(NewUpdatesIcon)
            AptIcon.show()
            AptIcon.setToolTip(tooltip_1_new_update_available)
            add_rightclick_actions()
            # Shows the pop up message only if not displayed before 
            if message_status == "not displayed":
                def show_message():
                    AptIcon.showMessage(popup_title, popup_msg_1_new_update_available)
                Timer.singleShot(1000, show_message)
                message_status = "displayed"
        else:
            AptIcon.setIcon(NewUpdatesIcon)
            AptIcon.show()
            tooltip_template=Template(tooltip_multiple_new_updates_available)
            tooltip_with_count=tooltip_template.substitute(count=text)
            AptIcon.setToolTip(tooltip_with_count)    
            add_rightclick_actions()
            # Shows the pop up message only if not displayed before 
            if message_status == "not displayed":
                # ~~~ Localize 1b ~~~
                # Use embedded count placeholder.
                popup_template=Template(popup_msg_multiple_new_updates_available)
                popup_with_count=popup_template.substitute(count=text)
                def show_message():
                    #AptIcon.showMessage(popup_title, popup_msg_multiple_new_updates_available_begin + text + popup_msg_multiple_new_updates_available_end)
                    AptIcon.showMessage(popup_title, popup_with_count)
                Timer.singleShot(1000, show_message)
                message_status = "displayed"
   
def start_synaptic():
    global Check_for_Updates_by_User
    run = subprocess.Popen(['/usr/bin/su-to-root -X -c synaptic'],shell=True).wait()
    Check_for_Updates_by_User = 'true'
    check_updates()

def viewandupgrade():
    global Check_for_Updates_by_User
    initialize_aptnotifier_prefs()
    
    # ~~~ Localize 2 ~~~

    # Accommodations for transformation from Python literals to Bash literals:
    #	t05: \\n will convert to \n
    #   t07: \\n will convert to \n
    #   t11: '( and )' moved outside of translatable string to protect from potential translator's typo
    #   t13: \\\"n\\\" will convert to \"n\" which will become "n" in shell (to avoid concatenating shell strings)

    # t01 thru t07, Yad 'View and Upgrade' strings 
    t01 = _("MX Apt Notifier--View and Upgrade, previewing: apt-get")
    t02 = _("use apt-get's --yes option for")
    t03 = _("automatically close terminal window when apt-get %s complete")
    t04 = _("switch to %s")
    t05 = _("Switches the type of Upgrade that will be performed, alternating back and forth between 'apt-get upgrade' and 'apt-get dist-upgrade'.")
    t06 = _("Reload")
    t07 = _("Reload the package information to become informed about new, removed or upgraded software packages. (apt-get update)")
    
    # t08, gksu dialog
    t08 = _("The action you requested needs <b>root privileges</b>. Please enter <b>root's</b> password below.")

    # t09 thru t13, strings for the upgrade/dist-upgrade script that runs in the terminal window    
    t09 = _("%s complete (or was canceled)")
    t10 = _("this terminal window can now be closed")
    t11 = "'(" + _("press any key to close") + ")'"
    t12 = _("Unneeded packages are installed that can be removed.")
    t13 = _("Running apt-get autoremove, if you are unsure type 'n'.")

    shellvar = (
	'    window_title="'			+ t01 + '"\n'
	'    use_apt_get_dash_dash_yes="'	+ t02 + '"\n'
	'    auto_close_window="'		+ t03 + '"\n'
	'    switch_to="'			+ t04 + '"\n'
	'    switch_tooltip="'			+ t05 + '"\n'
	'    reload="'				+ t06 + '"\n'
	'    reload_tooltip="'			+ t07 + '"\n'
	'    rootPasswordRequestMsg="'		+ t08 + '"\n'
	'    done1="'				+ t09 + '"\n'
	'    done2="'				+ t10 + '"\n'
	'    done3="'				+ t11 + '"\n'
	'    autoremovable_packages_msg1="'	+ t12 + '"\n'
	'    autoremovable_packages_msg2="'	+ t13 + '"\n'
	)
    
    script = '''#!/bin/bash
    
    #cancel updates available indication if 2 or more Release.reverify entries found
    #if [ $(ls -1 /var/lib/apt/lists/partial/ | grep Release.reverify$ | wc -l) -ge 2 ]; then exit; fi 

''' + shellvar + '''

    RunAptScriptInTerminal(){
    #for MEPIS remove "MX" branding from the $window_title string
    window_title=$(echo "$1"|sed 's/MX /'$(grep -o MX.*[1-9][0-9] /etc/issue|cut -c1-2)" "'/')

        TermXOffset="$(xwininfo -root|awk '/Width/{print $2/4}')"
        TermYOffset="$(xwininfo -root|awk '/Height/{print $2/4}')"
        G=" --geometry=80x25+"$TermXOffset"+"$TermYOffset
        I=" --icon=mnotify-some-""$(grep IconLook ~/.config/apt-notifierrc | cut -f2 -d=)"
        if [ "$2" = "" ]; then T=""; I=""; else T=" --title='""$(grep -o MX.*[1-9][0-9] /etc/issue|cut -c1-2)"" apt-notifier: apt-get "$2"'"; fi
        if (xprop -root | grep -q -i kde)
          then

            # Running KDE
            #
            # Can't get su-to-root to work in newer KDE's, so use kdesu for 
            # authentication.
            #  
            # If x-terminal-emulator is set to xfce4-terminal.wrapper, use     
            # xfce4-terminal instead because the --hold option doesn't work with
            # the wrapper. Also need to enclose the apt-get command in single 
            # quotes.
            #
            # If x-terminal-emulator is set to xterm, use konsole instead, if 
            # it's available (it should be).

            case $(readlink -e /usr/bin/x-terminal-emulator | xargs basename) in

              gnome-terminal.wrapper) if [ -e /usr/bin/konsole ]
                                        then
                                          $(kde4-config --path libexec)kdesu -c "konsole -e $3"
                                          sleep 5
                                          while [ "$(ps aux | grep [0-9]' konsole -e apt-get update')" != "" ]
                                            do
                                              sleep 1
                                            done
                                          sleep 1 
                                        else
                                          :
                                      fi
                                      ;;

                             konsole) $(kde4-config --path libexec)kdesu -c "konsole -e $3"
                                      sleep 5
                                      while [ "$(ps aux | grep [0-9]' konsole -e apt-get update')" != "" ]
                                        do
                                          sleep 1
                                        done
                                      sleep 1 
                                      ;;

                             roxterm) $(kde4-config --path libexec)kdesu -c "roxterm$G$T --separate -e $3"
                                      ;;

              xfce4-terminal.wrapper) $(kde4-config --path libexec)kdesu --noignorebutton -d -c "xfce4-terminal$G$I$T -e $3"
                                      ;;

                               xterm) if [ -e /usr/bin/konsole ]
                                        then
                                          $(kde4-config --path libexec)kdesu -c "konsole -e $3"
                                          sleep 5
                                          while [ "$(ps aux | grep [0-9]' konsole -e apt-get update')" != "" ]
                                            do
                                              sleep 1
                                            done
                                          sleep 1 
                                        else
                                          $(kde4-config --path libexec)kdesu -c "xterm -e $3"
                                      fi
                                      ;;

                                   *) $(kde4-config --path libexec)kdesu -c "x-terminal-emulator -e $3"
                                      sleep 5
                                      while [ "$(ps aux | grep [0-9]' konsole -e apt-get update')" != "" ]
                                        do
                                          sleep 1
                                        done
                                      sleep 1 
                                      ;;
            esac

          else

            # Running a non KDE desktop
            # 
            # Use su-to-root for authentication, it should end up using gksu.
            # 
            # If x-terminal-emulator is set to xfce4-terminal.wrapper, use 
            # xfce4-terminal instead because the --hold option doesn't work
            # with the wrapper. Also need to enclose the apt-get command in
            # single quotes.
            #
            # If x-terminal-emulator is set to xterm, use xfce4-terminal 
            # instead, if it's available (it is in MX)

            case $(readlink -e /usr/bin/x-terminal-emulator | xargs basename) in

              gnome-terminal.wrapper) su-to-root -X -c "gnome-terminal$G$T -e $3"
                                      ;;

                             konsole) su-to-root -X -c "konsole -e $3"
                                      sleep 5
                                      while [ "$(ps aux | grep [0-9]' konsole -e apt-get update')" != "" ]
                                        do
                                          sleep 1
                                        done
                                      sleep 1 
                                      ;;

                             roxterm) su-to-root -X -c "roxterm$G$T --separate -e $3"
                                      ;;

              xfce4-terminal.wrapper) if [ -x $(whereis gksu | awk '{print $2}') ]
                                        then
                                          gksu --su-mode -m "$rootPasswordRequestMsg""\n\n'apt-get $2'" "xfce4-terminal$G$I$T -e $3"
                                        else
                                          su-to-root -X -c "xfce4-terminal$G$I$T -e $3"
                                      fi                                      
                                      ;;

                               xterm) if [ -e /usr/bin/xfce4-terminal ]
                                        then
                                          su-to-root -X -c "xfce4-terminal$G$I$T -e $3"
                                        else
                                          su-to-root -X -c "xterm -e $3"
                                      fi
                                      ;;

                                   *) su-to-root -X -c "x-terminal-emulator -e $3"
                                      ;;

            esac
        fi
    }    
        
    DoUpgrade(){
      case $1 in
        0)
        BP="1"
        chmod +x $TMP/upgradeScript
        RunAptScriptInTerminal "$window_title" "$UpgradeType" "$TMP/upgradeScript"
        ;;

        2)
        BP="1"
        ;;
        
        4)
        BP="0"
        sed -i 's/UpgradeType='$UpgradeType'/UpgradeType='$OtherUpgradeType'/' ~/.config/apt-notifierrc
        ;;
        
        8)
        BP="0"
        #chmod +x $TMP/upgradeScript
        RunAptScriptInTerminal "" "update" "'apt-get update'"
        sleep 1
        ;;
        
        *)
        BP="1"
        ;;
        
       esac 
    }

    BP="0"
    while [ $BP != "1" ]
      do

        UpgradeType=$(grep ^UpgradeType ~/.config/apt-notifierrc | cut -f2 -d=)
        if [ "$UpgradeType" = "upgrade"      ]; then
          OtherUpgradeType="dist-upgrade"
        fi
        if [ "$UpgradeType" = "dist-upgrade" ]; then
          OtherUpgradeType="upgrade"
        fi
  
        UpgradeAssumeYes=$(grep ^UpgradeAssumeYes ~/.config/apt-notifierrc | cut -f2 -d=)
        UpgradeAutoClose=$(grep ^UpgradeAutoClose ~/.config/apt-notifierrc | cut -f2 -d=)
      
        TMP=$(mktemp -d /tmp/apt-notifier.XXXXXX)
        echo "apt-get $UpgradeType" > "$TMP"/upgrades
        
        #The following 40 or so lines (down to the "APT_CONFIG" line) create a temporary etc/apt folder and subfolders
        #that for the most part match the root owned /etc/apt folder and it's subfolders.
        #
        #A symlink to /var/synaptic/preferences symlink ("$TMP"/etc/apt/preferences.d/synaptic-pins) will be created
        #if there isn't one already (note: the non-root user wouldn't be able to create one in /etc/apt/preferences.d/).
        #
        #With a /var/synaptic/preferences symlink in place, no longer need to remove the lines with Synaptic pinned packages
        #from the "$TMP"/upgrades file to keep them from being displayed in the 'View and Upgrade' window, also no longer
        #need to correct the upgrades count after removing the lines with the pinned updates.
        
        #create the etc/apt/*.d subdirectories in the temporary directory ("$TMP")
        for i in $(find /etc/apt -name *.d); do mkdir -p "$TMP"/$(echo $i | cut -f2- -d/); done

        #create symlinks to the files in /etc/apt and it's subdirectories with exception of /etc/apt and /etc/apt/apt.conf  
        for i in $(find /etc/apt | grep -v -e .d$ -e apt.conf$ -e apt$); do ln -s $i "$TMP"/$(echo $i | cut -f2- -d/) 2>/dev/null; done

        #in etc/preferences test to see if there's a symlink to /var/lib/synaptic/preferences
        ls -l /etc/apt/preferences* | grep ^l | grep -m1 /var/lib/synaptic/preferences$ -q

        #if there isn't, create one if there are synaptic pinned packages
        if [ $? -eq 1 ]
          then
            if [ -s /var/lib/synaptic/preferences ]
              then ln -s /var/lib/synaptic/preferences "$TMP"/etc/apt/preferences.d/synaptic-pins 2>/dev/null
            fi
        fi

        #create a apt.conf in the temp directory by copying existing /etc/apt/apt.conf to it
        [ ! -e /etc/apt/apt.conf ] || cp /etc/apt/apt.conf "$TMP"/apt.conf

        #in apt.conf file set Dir to the path of the temp directory
        echo 'Dir "'"$TMP"'/";' >> "$TMP"/apt.conf
        #set Dir::State::* and Dir::Cache::* to the existing ones in /var/lib/apt, /var/lib/dpkg and /var/cache/apt
        echo 'Dir::State "/var/lib/apt/";' >> "$TMP"/apt.conf
        echo 'Dir::State::Lists "/var/lib/apt/lists/";' >> "$TMP"/apt.conf
        echo 'Dir::State::status "/var/lib/dpkg/status";' >> "$TMP"/apt.conf
        echo 'Dir::State::extended_states "/var/lib/apt/extended_states";' >> "$TMP"/apt.conf
        echo 'Dir::Cache "/var/cache/apt/";' >> "$TMP"/apt.conf
        echo 'Dir::Cache::Archives "/var/cache/apt/archives";' >> "$TMP"/apt.conf
        echo 'Dir::Cache::srcpkgcache "/var/cache/apt/srcpkgcache.bin";' >> "$TMP"/apt.conf
        echo 'Dir::Cache::pkgcache "/var/cache/apt/pkgcache.bin";' >> "$TMP"/apt.conf

        APT_CONFIG="$TMP"/apt.conf apt-get -o Debug::NoLocking=true --trivial-only -V $UpgradeType 2>/dev/null >> "$TMP"/upgrades

        #fix to display epochs
        #for i in $(grep [[:space:]]'=>'[[:space:]] "$TMP"/upgrades | awk '{print $1}')
        #do
        #  withoutEpoch="$(grep [[:space:]]$i[[:space:]] "$TMP"/upgrades | awk '{print $2}')"
        #  withEpoch="(""$(apt-cache policy $i | head -2 | tail -1 | awk '{print $NF}')"
        #  sed -i 's/'"$withoutEpoch"'/'"$withEpoch"'/' "$TMP"/upgrades
        #  withoutEpoch="$(grep [[:space:]]$i[[:space:]] "$TMP"/upgrades | awk '{print $4}')"
        #  withEpoch="$(apt-cache policy $i | head -3 | tail -1 | awk '{print $NF}')"")"
        #  sed -i 's/'"$withoutEpoch"'/'"$withEpoch"'/' "$TMP"/upgrades
        #done

        # ~~~ Localize 2a ~~~
        # Format switch label. switch_to contains %s. eg "switch to %s" or "zu %s wechseln"
        # Result output to switch_label could be eg "switch to 'apt-get upgrade'"
        # or "zu 'apt-get dist-upgrade' wechseln'"
        # Should be able to use statement like:
        #      printf -v switch_label "$switch_to" "$switch_type"
        # But fails, so use sed instead.
        # Format auto close message in same way.

        switch_type="'apt-get ""$OtherUpgradeType""'"
        switch_label=$(echo "$switch_to" | sed 's/%s/'"$switch_type"'/')
        auto_close_label=$(echo "$auto_close_window" | sed 's/%s/'"$UpgradeType"'/')

        yad \\
        --window-icon=/usr/share/icons/mnotify-some-"$(grep IconLook ~/.config/apt-notifierrc | cut -f2 -d=)".png \\
        --width=640 \\
        --height=480 \\
        --center \\
        --title "$(echo "$window_title"|sed 's/MX /'$(grep -o MX.*[1-9][0-9] /etc/issue|cut -c1-2)" "'/') $UpgradeType" \\
        --form \\
          --field :TXT "$(sed 's/^/  /' "$TMP"/upgrades)" \\
          --field="$use_apt_get_dash_dash_yes $UpgradeType":CHK $UpgradeAssumeYes \\
          --field="$auto_close_label":CHK $UpgradeAutoClose \\
        --button "$switch_label"!!"$switch_tooltip":4 \\
        --button 'apt-get '"$UpgradeType"!mnotify-some-"$(grep IconLook ~/.config/apt-notifierrc | cut -f2 -d=)"!:0 \\
        --button "$reload"!reload!"$reload_tooltip":8 \\
        --button gtk-cancel:2 \\
        --buttons-layout=spread \\
        2>/dev/null \\
        > "$TMP"/results 

        echo $?>>"$TMP"/results

        # if the View and Upgrade yad window was closed by one of it's 4 buttons, 
        # then update the UpgradeAssumeYes & UpgradeAutoClose flags in the 
        # ~/.config/apt-notifierrc file to match the checkboxes
        if [ $(tail -n1 "$TMP"/results) -eq 0 ]||\\
           [ $(tail -n1 "$TMP"/results) -eq 2 ]||\\
           [ $(tail -n1 "$TMP"/results) -eq 4 ]||\\
           [ $(tail -n1 "$TMP"/results) -eq 8 ];
          then
            if [ "$(head -n1 "$TMP"/results | rev | awk -F \| '{ print $3}' | rev)" = "TRUE" ];
              then
                grep UpgradeAssumeYes=true  ~/.config/apt-notifierrc -q || sed -i 's/UpgradeAssumeYes=false/UpgradeAssumeYes=true/' ~/.config/apt-notifierrc
              else
                grep UpgradeAssumeYes=false ~/.config/apt-notifierrc -q || sed -i 's/UpgradeAssumeYes=true/UpgradeAssumeYes=false/' ~/.config/apt-notifierrc
            fi
            if [ "$(head -n1 "$TMP"/results | rev | awk -F \| '{ print $2}' | rev)" = "TRUE" ];
              then
                grep UpgradeAutoClose=true  ~/.config/apt-notifierrc -q || sed -i 's/UpgradeAutoClose=false/UpgradeAutoClose=true/' ~/.config/apt-notifierrc
              else
                grep UpgradeAutoClose=false ~/.config/apt-notifierrc -q || sed -i 's/UpgradeAutoClose=true/UpgradeAutoClose=false/' ~/.config/apt-notifierrc
            fi
          else
            :
        fi

        # refresh UpgradeAssumeYes & UpgradeAutoClose 
        UpgradeAssumeYes=$(grep ^UpgradeAssumeYes ~/.config/apt-notifierrc | cut -f2 -d=)
        UpgradeAutoClose=$(grep ^UpgradeAutoClose ~/.config/apt-notifierrc | cut -f2 -d=)
        
        if [ $(tail -n1 "$TMP"/results) -eq 8 ];
          then
            # build a upgrade script to do a apt-get update
            echo "#!/bin/bash"> "$TMP"/upgradeScript
            echo "echo 'apt-get update'">> "$TMP"/upgradeScript
            echo "apt-get update">> "$TMP"/upgradeScript

          else
            # build a upgrade script to do the apt-get upgrade (or dist-upgrade)
            echo "#!/bin/bash"> "$TMP"/upgradeScript
            echo "echo 'apt-get '"$UpgradeType>> "$TMP"/upgradeScript
            echo 'find /etc/apt/preferences.d | grep -E synaptic-[0-9a-zA-Z]{6}-pins | xargs rm -f'>> "$TMP"/upgradeScript 
            echo 'if [ -f /var/lib/synaptic/preferences -a -s /var/lib/synaptic/preferences ]'>> "$TMP"/upgradeScript
            echo '  then '>> "$TMP"/upgradeScript
            echo '    SynapticPins=$(mktemp /etc/apt/preferences.d/synaptic-XXXXXX-pins)'>> "$TMP"/upgradeScript
            echo '    ln -sf /var/lib/synaptic/preferences "$SynapticPins" 2>/dev/null'>> "$TMP"/upgradeScript
            echo 'fi'>> "$TMP"/upgradeScript
            echo 'file "$SynapticPins" | cut -f2- -d" " | grep -e"broken symbolic link" -e"empty" -q '>> "$TMP"/upgradeScript
            echo 'if [ $? -eq 0 ]; then find /etc/apt/preferences.d | grep -E synaptic-[0-9a-zA-Z]{6}-pins | xargs rm -f; fi'>> "$TMP"/upgradeScript
            if [ "$UpgradeAssumeYes" = "true" ];
              then
                echo "apt-get --assume-yes -V "$UpgradeType>> "$TMP"/upgradeScript
              else
                echo "apt-get -V "$UpgradeType>> "$TMP"/upgradeScript
            fi
            grep ^CheckForAutoRemoves=true ~/.config/apt-notifierrc -q
            if [ $? -eq 0 ]
              then
                echo "echo">> "$TMP"/upgradeScript
                echo 'apt-get autoremove -s | grep ^Remv -q'>> "$TMP"/upgradeScript
                echo 'if [ $? -eq 0 ]; '>> "$TMP"/upgradeScript
                echo '  then'>> "$TMP"/upgradeScript
                echo 'echo "'"$autoremovable_packages_msg1"'"'>> "$TMP"/upgradeScript
                echo 'echo "'"$autoremovable_packages_msg2"'"'>> "$TMP"/upgradeScript
                echo 'apt-get autoremove -qV'>> "$TMP"/upgradeScript
                echo '  else'>> "$TMP"/upgradeScript
                echo '    :'>> "$TMP"/upgradeScript
                echo 'fi'>> "$TMP"/upgradeScript
              else
                :
            fi
            echo "echo">> "$TMP"/upgradeScript
            echo 'find /etc/apt/preferences.d | grep -E synaptic-[0-9a-zA-Z]{6}-pins | xargs rm -f'>> "$TMP"/upgradeScript
            
            # ~~~ Localize 2b ~~~

            donetype="apt-get $UpgradeType"
            donetext=$(echo "$done1" | sed 's/%s/'"$donetype"'/')
            echo 'echo "'"$donetext"'"'>> "$TMP"/upgradeScript
            echo "echo">> "$TMP"/upgradeScript

            if [ "$UpgradeAutoClose" = "true" ];
              then
                echo "sleep 1">> "$TMP"/upgradeScript
                echo "exit 0">> "$TMP"/upgradeScript
              else
                echo "echo -n $done2' '">> "$TMP"/upgradeScript
                echo "read -sn 1 -p $done3 -t 999999999">> "$TMP"/upgradeScript
                echo "echo">> "$TMP"/upgradeScript
                echo "exit 0">> "$TMP"/upgradeScript
            fi
        fi

        DoUpgrade $(tail -n1 "$TMP"/results)

        rm -rf "$TMP"

      done

    sleep 2
    PID=`pidof apt-get | cut -f 1 -d " "`
    if [ $PID ]; then
        while (ps -p $PID > /dev/null); do
            sleep 2
        done
    fi
    '''
    script_file = tempfile.NamedTemporaryFile('wt')
    script_file.write(script)
    script_file.flush()
    run = subprocess.Popen(['sh %s' % script_file.name],shell=True).wait()
    script_file.close()
    Check_for_Updates_by_User = 'true'
    check_updates()

def initialize_aptnotifier_prefs():

    """Create/initialize preferences in the ~/.config/apt-notifierrc file  """
    """if they don't already exist. Remove multiple entries and those that """
    """appear to be invalid.                                               """ 

    script = '''#! /bin/bash

    #test if ~/.config/apt-notifierrc contains a UpgradeType=* line and that it's a valid entry
    grep -q -e ^"UpgradeType=upgrade" -e^"UpgradeType=dist-upgrade" ~/.config/apt-notifierrc
    if [ "$?" -eq 0 ]
      then
      #contains a valid entry so do nothing
        :
      else
      #
      #if a UpgradeType=* line not present,
      #or not equal to "upgrade" or "dist-upgrade"
      #initially set it to "UpgradeType=dist-upgrade"
      #also delete multiple entries or what appears to be invalid entries
      sed -i '/.*UpgradeType.*/Id' ~/.config/apt-notifierrc 
      echo "UpgradeType=dist-upgrade">> ~/.config/apt-notifierrc
    fi

    #test if ~/.config/apt-notifierrc contains a UpgradeAssumeYes=* line and that it's a valid entry
    grep -q -e ^"UpgradeAssumeYes=true" -e^"UpgradeAssumeYes=false" ~/.config/apt-notifierrc
    if [ "$?" -eq 0 ]
      then
      #contains a valid entry so do nothing
        :
      else
      #
      #if a UpgradeAssumeYes=* line not present,
      #or not equal to "true" or "false"
      #initially set it to "UpgradeAssumeYes=false"
      #also delete multiple entries or what appears to be invalid entries
      sed -i '/.*UpgradeAssumeYes.*/Id' ~/.config/apt-notifierrc 
      echo "UpgradeAssumeYes=false">> ~/.config/apt-notifierrc
    fi

    #test if ~/.config/apt-notifierrc contains a UpgradeAutoClose=* line and that it's a valid entry
    grep -q -e ^"UpgradeAutoClose=true" -e^"UpgradeAutoClose=false" ~/.config/apt-notifierrc
    if [ "$?" -eq 0 ]
      then
      #contains a valid entry so do nothing
        :
      else
      #
      #if a UpgradeAutoClose=* line not present,
      #or not equal to "true" or "false"
      #intially set it to "UpgradeAutoClose=false"
      #also delete multiple entries or what appears to be invalid entries
      sed -i '/.*UpgradeAutoClose.*/Id' ~/.config/apt-notifierrc 
      echo "UpgradeAutoClose=false">> ~/.config/apt-notifierrc
    fi

    #test if ~/.config/apt-notifierrc contains a LeftClick=* line and that it's a valid entry
    grep -q -e ^"LeftClick=ViewAndUpgrade" -e^"LeftClick=Synaptic" ~/.config/apt-notifierrc
    if [ "$?" -eq 0 ]
      then
      #contains a valid entry so do nothing
        :
      else
      #
      #if a LeftClick line not present,
      #or not equal to "ViewAndUpgrade" or "Synaptic"
      #initially set it to "LeftClick=ViewAndUpgrade"
      #also delete multiple entries or what appears to be invalid entries
      sed -i '/.*LeftClick.*/Id' ~/.config/apt-notifierrc 
      echo "LeftClick=ViewAndUpgrade">> ~/.config/apt-notifierrc
    fi

    #test if ~/.config/apt-notifierrc contains a CheckForAutoRemoves=* line and that it's a valid entry
    grep -q -e ^"CheckForAutoRemoves=true" -e^"CheckForAutoRemoves=false" ~/.config/apt-notifierrc
    if [ "$?" -eq 0 ]
      then
      #contains a valid entry so do nothing
        :
      else
      #
      #if a CheckForAutoRemoves=* line not present,
      #or not equal to "true" or "false"
      #intially set it to "CheckForAutoRemoves=false"
      #also delete multiple entries or what appears to be invalid entries
      sed -i '/.*CheckForAutoRemoves.*/Id' ~/.config/apt-notifierrc 
      echo "CheckForAutoRemoves=false">> ~/.config/apt-notifierrc
    fi

    #test if ~/.config/apt-notifierrc contains a IconLook=* line and that it's a valid entry
    grep -q -e ^"IconLook=wireframe" -e^"IconLook=classic" -e^"IconLook=pulse" ~/.config/apt-notifierrc
    if [ "$?" -eq 0 ]
      then
      #contains a valid entry so do nothing
        :
      else
      #
      #delete multiple entries or what appears to be invalid entries
      sed -i '/.*IconLook.*/Id' ~/.config/apt-notifierrc 
      #
      #if a IconLook=* line not present,
      #or not equal to "wireframe" or "classic" or "pulse", then have default as follows for the various MX releases
      #
       case $(grep DISTRIB_RELEASE /etc/lsb-release | grep -Eo [0-9.]+) in
         14  ) IconDefault="classic" ;;
         15  ) IconDefault="classic" ;;
         16  ) IconDefault="wireframe"    ;;
	     16.1) IconDefault="wireframe"    ;;
            *) IconDefault="classic" ;;
       esac
       echo "IconLook=$IconDefault">> ~/.config/apt-notifierrc
    fi

    #test to see if ~/.config/apt-notifierrc contains any blank lines or lines with only whitespace
    grep -q ^[[:space:]]*$ ~/.config/apt-notifierrc 
    if [ "$?" = "0" ]
      then
      #cleanup any blank lines or lines with only whitespace
        sed -i '/^[[:space:]]*$/d' ~/.config/apt-notifierrc
      else
      #no blank lines or lines with only whitespace so do nothing
        :
    fi

    [ -e ~/.local/share/applications/apt-notifier-menu.desktop ] || cp /usr/share/applications/apt-notifier-menu.desktop ~/.local/share/applications/apt-notifier-menu.desktop

    grep $(grep IconLook ~/.config/apt-notifierrc | cut -f2 -d=) ~/.local/share/applications/apt-notifier-menu.desktop -q
    [ $? -eq 0 ] || sed -i 's/mnotify-some.*/mnotify-some-'"$(grep IconLook ~/.config/apt-notifierrc | cut -f2 -d=)"'/' ~/.local/share/applications/apt-notifier-menu.desktop

    [ -e ~/.local/share/applications/mx-apt-notifier-menu.desktop ] || cp /usr/share/applications/mx-apt-notifier-menu.desktop ~/.local/share/applications/mx-apt-notifier-menu.desktop

    grep $(grep IconLook ~/.config/apt-notifierrc | cut -f2 -d=) ~/.local/share/applications/mx-apt-notifier-menu.desktop -q 
    [ $? -eq 0 ] || sed -i 's/mnotify-some.*/mnotify-some-'"$(grep IconLook ~/.config/apt-notifierrc | cut -f2 -d=)"'/' ~/.local/share/applications/mx-apt-notifier-menu.desktop

    '''

    script_file = tempfile.NamedTemporaryFile('wt')
    script_file.write(script)
    script_file.flush()
    run = subprocess.Popen(['sh %s' % script_file.name],shell=True).wait()
    script_file.close()


def aptnotifier_prefs():
    global Check_for_Updates_by_User
    initialize_aptnotifier_prefs()
    
    # ~~~ Localize 3 ~~~

    t01 = _("MX Apt Notifier preferences")
    t02 = _("Upgrade behaviour   (also affects notification count)")
    t03 = _("Left-click behaviour   (when updates are available)")
    t04 = _("Other options")
    t05 = _("opens Synaptic")
    t06 = _("opens MX Apt Notifier 'View and Upgrade' window")
    t07 = _("use apt-get's --yes option for upgrade/dist-upgrade")
    t08 = _("automatically close terminal window when apt-get upgrade/dist-upgrade complete")
    t09 = _("check for autoremovable packages after apt-get upgrade/dist-upgrade")
    t10 = _("Icons")
    t11 = _("classic")
    t12 = _("pulse")
 
    shellvar = (
	'    window_title="'				+ t01 + '"\n'
	'    frame_upgrade_behaviour="'			+ t02 + '"\n'
	'    frame_left_click_behaviour="'		+ t03 + '"\n'
	'    frame_other_options="'			+ t04 + '"\n'
	'    left_click_Synaptic="'			+ t05 + '"\n'
	'    left_click_ViewandUpgrade="'		+ t06 + '"\n'
	'    use_apt_get_dash_dash_yes="'		+ t07 + '"\n'
	'    auto_close_term_window_when_complete="' 	+ t08 + '"\n'
	'    check_for_autoremoves="'			+ t09 + '"\n'
	'    frame_Icons="'				+ t10 + '"\n'
	'    label_classic="'				+ t11 + '"\n'
	'    label_pulse="'				+ t12 + '"\n'
	)
    
    script = '''#! /bin/bash
''' + shellvar + '''    

    #for MEPIS remove "MX" branding from the $window_title and $left_click_ViewandUpgrade strings
    window_title=$(echo "$window_title"|sed 's/MX /'$(grep -o MX.*[1-9][0-9] /etc/issue|cut -c1-2)" "'/')
    left_click_ViewandUpgrade=$(echo "$left_click_ViewandUpgrade"|sed 's/MX /'$(grep -o MX-[1-9][0-9] /etc/issue|cut -c1-2)" "'/')
    IconLookBegin=$(grep IconLook ~/.config/apt-notifierrc | cut -f2 -d=)
    TMP=$(mktemp -d /tmp/apt_notifier_preferences_dialog.XXXXXX)
    touch "$TMP"/output
    cat << EOF > "$TMP"/DIALOG
    <window title="@title@" icon-name="@mnotify-some@">
      <vbox>
        <frame @upgrade_behaviour@>
          <frame>
            <radiobutton active="@UpgradeBehaviourAptGetUpgrade@">
              <label>"apt-get upgrade"</label>
              <variable>UpgradeType_upgrade</variable>
              <action>:</action>
            </radiobutton>
            <radiobutton active="@UpgradeBehaviourAptGetDistUpgrade@">
              <label>"apt-get dist-upgrade"</label>
              <variable>UpgradeType_dist-upgrade</variable>
              <action>:</action>
            </radiobutton>
          </frame>
        </frame>
        <vseparator></vseparator>
        <frame @leftclick_behaviour@>
          <frame>
            <radiobutton active="@LeftClickBehaviourSynaptic@">
              <label>@opens_Synaptic@</label>
              <variable>LeftClickSynaptic</variable>
              <action>:</action>
            </radiobutton>
            <radiobutton active="@LeftClickBehaviourViewAndUpgrade@">
              <label>@opens_View_and_Upgrade@</label>
              <variable>LeftClickViewAndUpgrade</variable>
              <action>:</action>
            </radiobutton>
          </frame>
        </frame>
        <frame @Other_options@>
        <frame>
          <checkbox active="@UpgradeAssumeYes@">
            <label>@use_apt_get_yes@</label>
            <variable>UpgradeAssumeYes</variable>
            <action>:</action>
          </checkbox>
        </frame>
        <frame>
          <checkbox active="@UpgradeAutoClose@">
            <label>@auto_close_term_window@</label>
            <variable>UpgradeAutoClose</variable>
            <action>:</action>
          </checkbox>
        </frame>
        <frame>
          <checkbox active="@CheckForAutoRemoves@">
            <label>@check_for_autoremoves@</label>
            <variable>CheckForAutoRemoves</variable>
            <action>:</action>
          </checkbox>
        </frame>
        <vseparator></vseparator>
        </frame>
        <frame @Icons@>
          <hbox homogeneous="true">
          <vbox>
            <radiobutton active="@IconLookWireframe@">
              <label>"wireframe"</label>
              <variable>IconLook_wireframe</variable>
              <action>:</action>
            </radiobutton>
            <radiobutton active="@IconLookClassic@">
              <label>@classic@</label>
              <variable>IconLook_classic</variable>
              <action>:</action>
            </radiobutton>
            <radiobutton active="@IconLookPulse@">
              <label>@pulse@</label>
              <variable>IconLook_pulse</variable>
              <action>:</action>
            </radiobutton>
          </vbox>
          <vbox>
            <pixmap icon_size="2"><input file>"/usr/share/icons/mnotify-some-wireframe.png"</input></pixmap>
            <pixmap icon_size="2"><input file>"/usr/share/icons/mnotify-some-classic.png"</input></pixmap>
            <pixmap icon_size="2"><input file>"/usr/share/icons/mnotify-some-pulse.png"</input></pixmap>
          </vbox>
          <vbox>
            <pixmap icon_size="2"><input file>"/usr/share/icons/mnotify-none-wireframe.png"</input></pixmap>
            <pixmap icon_size="2"><input file>"/usr/share/icons/mnotify-none-classic.png"</input></pixmap>
            <pixmap icon_size="2"><input file>"/usr/share/icons/mnotify-none-pulse.png"</input></pixmap>
          </vbox>
          </hbox>
        </frame>
      <vseparator></vseparator>
      <hbox>
        <button ok> </button>
        <button cancel> </button>
      </hbox>
      </vbox>
    </window>
EOF

    # edit translateable strings placeholders in "$TMP"/DIALOG
    sed -i 's/@title@/'"$window_title"'/' "$TMP"/DIALOG
    sed -i 's/@upgrade_behaviour@/'"$frame_upgrade_behaviour""   "'/' "$TMP"/DIALOG
    sed -i 's/@leftclick_behaviour@/'"$frame_left_click_behaviour""   "'/' "$TMP"/DIALOG
    sed -i 's/@Other_options@/'"$frame_other_options""   "'/' "$TMP"/DIALOG
    sed -i 's/@Icons@/'"$frame_Icons""   "'/' "$TMP"/DIALOG
    sed -i 's/@opens_Synaptic@/"'"$left_click_Synaptic"'"/' "$TMP"/DIALOG
    sed -i 's/@opens_View_and_Upgrade@/"'"$left_click_ViewandUpgrade"'"/' "$TMP"/DIALOG
    sed -i 's|@use_apt_get_yes@|"'"$use_apt_get_dash_dash_yes"'"|' "$TMP"/DIALOG
    sed -i 's|@auto_close_term_window@|"'"$auto_close_term_window_when_complete"'"|' "$TMP"/DIALOG
    sed -i 's|@check_for_autoremoves@|"'"$check_for_autoremoves"'"|' "$TMP"/DIALOG
    sed -i 's/@classic@/"'"$label_classic"'"/' "$TMP"/DIALOG
    sed -i 's/@pulse@/"'"$label_pulse"'"/' "$TMP"/DIALOG

    # edit placeholders in "$TMP"/DIALOG to set initial settings of the radiobuttons & checkboxes 
    sed -i 's/@UpgradeBehaviourAptGetUpgrade@/'$(if [ $(grep UpgradeType=upgrade ~/.config/apt-notifierrc) ]; then echo -n true; else echo -n false; fi)'/' "$TMP"/DIALOG
    sed -i 's/@UpgradeBehaviourAptGetDistUpgrade@/'$(if [ $(grep UpgradeType=dist-upgrade ~/.config/apt-notifierrc) ]; then echo -n true; else echo -n false; fi)'/' "$TMP"/DIALOG
    sed -i 's/@LeftClickBehaviourSynaptic@/'$(if [ $(grep LeftClick=Synaptic ~/.config/apt-notifierrc) ]; then echo -n true; else echo -n false; fi)'/' "$TMP"/DIALOG
    sed -i 's/@LeftClickBehaviourViewAndUpgrade@/'$(if [ $(grep LeftClick=ViewAndUpgrade ~/.config/apt-notifierrc) ]; then echo -n true; else echo -n false; fi)'/' "$TMP"/DIALOG
    sed -i 's/@UpgradeAssumeYes@/'$(grep UpgradeAssumeYes ~/.config/apt-notifierrc | cut -f2 -d=)'/' "$TMP"/DIALOG
    sed -i 's/@UpgradeAutoClose@/'$(grep UpgradeAutoClose ~/.config/apt-notifierrc | cut -f2 -d=)'/' "$TMP"/DIALOG
    sed -i 's/@CheckForAutoRemoves@/'$(grep CheckForAutoRemoves ~/.config/apt-notifierrc | cut -f2 -d=)'/' "$TMP"/DIALOG
    sed -i 's/@IconLookWireframe@/'$(if [ $(grep IconLook=wireframe ~/.config/apt-notifierrc) ]; then echo -n true; else echo -n false; fi)'/' "$TMP"/DIALOG
    sed -i 's/@IconLookClassic@/'$(if [ $(grep IconLook=classic ~/.config/apt-notifierrc) ]; then echo -n true; else echo -n false; fi)'/' "$TMP"/DIALOG
    sed -i 's/@IconLookPulse@/'$(if [ $(grep IconLook=pulse ~/.config/apt-notifierrc) ]; then echo -n true; else echo -n false; fi)'/' "$TMP"/DIALOG

    # edit placeholder for window icon placeholder in "$TMP"/DIALOG
    sed -i 's/@mnotify-some@/mnotify-some-'$(grep IconLook ~/.config/apt-notifierrc | cut -f2 -d= | xargs echo -n)'/' "$TMP"/DIALOG

    gtkdialog --file="$TMP"/DIALOG >> "$TMP"/output

    grep -q EXIT=.*OK.* "$TMP"/output

    if [ "$?" -eq 0 ];
      then
        if [ $(grep UpgradeType_upgrade=.*true.*      "$TMP"/output) ]; then sed -i 's/UpgradeType=dist-upgrade/UpgradeType=upgrade/'       ~/.config/apt-notifierrc; fi
        if [ $(grep UpgradeType_dist-upgrade=.*true.* "$TMP"/output) ]; then sed -i 's/UpgradeType=upgrade/UpgradeType=dist-upgrade/'       ~/.config/apt-notifierrc; fi
        if [ $(grep LeftClickViewAndUpgrade=.*true.*  "$TMP"/output) ]; then sed -i 's/LeftClick=Synaptic/LeftClick=ViewAndUpgrade/'        ~/.config/apt-notifierrc; fi
        if [ $(grep LeftClickSynaptic=.*true.*        "$TMP"/output) ]; then sed -i 's/LeftClick=ViewAndUpgrade/LeftClick=Synaptic/'        ~/.config/apt-notifierrc; fi
        if [ $(grep UpgradeAssumeYes=.*false.*        "$TMP"/output) ]; then sed -i 's/UpgradeAssumeYes=true/UpgradeAssumeYes=false/'       ~/.config/apt-notifierrc; fi
        if [ $(grep UpgradeAssumeYes=.*true.*         "$TMP"/output) ]; then sed -i 's/UpgradeAssumeYes=false/UpgradeAssumeYes=true/'       ~/.config/apt-notifierrc; fi
        if [ $(grep UpgradeAutoClose=.*false.*        "$TMP"/output) ]; then sed -i 's/UpgradeAutoClose=true/UpgradeAutoClose=false/'       ~/.config/apt-notifierrc; fi
        if [ $(grep UpgradeAutoClose=.*true.*         "$TMP"/output) ]; then sed -i 's/UpgradeAutoClose=false/UpgradeAutoClose=true/'       ~/.config/apt-notifierrc; fi
        if [ $(grep CheckForAutoRemoves=.*false.*     "$TMP"/output) ]; then sed -i 's/CheckForAutoRemoves=true/CheckForAutoRemoves=false/' ~/.config/apt-notifierrc; fi
        if [ $(grep CheckForAutoRemoves=.*true.*      "$TMP"/output) ]; then sed -i 's/CheckForAutoRemoves=false/CheckForAutoRemoves=true/' ~/.config/apt-notifierrc; fi
        if [ $(grep IconLook_wireframe=.*true.*            "$TMP"/output) ]; then sed -i 's/IconLook=classic/IconLook=wireframe/'                     ~/.config/apt-notifierrc; fi
        if [ $(grep IconLook_wireframe=.*true.*            "$TMP"/output) ]; then sed -i 's/IconLook=pulse/IconLook=wireframe/'                       ~/.config/apt-notifierrc; fi
        if [ $(grep IconLook_classic=.*true.*         "$TMP"/output) ]; then sed -i 's/IconLook=wireframe/IconLook=classic/'                     ~/.config/apt-notifierrc; fi
        if [ $(grep IconLook_classic=.*true.*         "$TMP"/output) ]; then sed -i 's/IconLook=pulse/IconLook=classic/'                    ~/.config/apt-notifierrc; fi
        if [ $(grep IconLook_pulse=.*true.*           "$TMP"/output) ]; then sed -i 's/IconLook=wireframe/IconLook=pulse/'                       ~/.config/apt-notifierrc; fi
        if [ $(grep IconLook_pulse=.*true.*           "$TMP"/output) ]; then sed -i 's/IconLook=classic/IconLook=pulse/'                    ~/.config/apt-notifierrc; fi
     else
        :
    fi

    rm -rf "$TMP"

    #update Icon= line in .local apt-notifier-menu.desktop file if icon not same as IconLook config setting in ~/.config/apt-notifierrc file
    grep $(grep IconLook ~/.config/apt-notifierrc | cut -f2 -d=) ~/.local/share/applications/apt-notifier-menu.desktop -q
    [ $? -eq 0 ] || sed -i 's/mnotify-some.*/mnotify-some-'"$(grep IconLook ~/.config/apt-notifierrc | cut -f2 -d=)"'/' ~/.local/share/applications/apt-notifier-menu.desktop

    #update Icon= line in .local mx-apt-notifier-menu.desktop file if icon not same as IconLook config setting in ~/.config/apt-notifierrc file
    grep $(grep IconLook ~/.config/apt-notifierrc | cut -f2 -d=) ~/.local/share/applications/mx-apt-notifier-menu.desktop -q 
    [ $? -eq 0 ] || sed -i 's/mnotify-some.*/mnotify-some-'"$(grep IconLook ~/.config/apt-notifierrc | cut -f2 -d=)"'/' ~/.local/share/applications/mx-apt-notifier-menu.desktop

    #restart apt-notifier if IconLook setting has been changed 
    if [ "$(grep IconLook ~/.config/apt-notifierrc | cut -f2 -d=)" != "$IconLookBegin" ]
      then
        apt-notifier-unhide-Icon
    fi

    '''
    script_file = tempfile.NamedTemporaryFile('wt')
    script_file.write(script)
    script_file.flush()
    run = subprocess.Popen(['sh %s' % script_file.name],shell=True).wait()
    script_file.close()
    Check_for_Updates_by_User = 'true'
    check_updates()

def apt_history():
    global Check_for_Updates_by_User

    # ~~~ Localize 5 ~~~

    t01 = _("Apt History")
    shellvar = '    AptHistory="' + t01 + '"\n'

    script = '''#! /bin/bash
''' + shellvar + '''
    
    TMP=$(mktemp -d /tmp/apt_history.XXXXXX)
    
    apt-history | sed 's/:all/ all/;s/:i386/ i386/;s/:amd64/ amd64/' | column -t > "$TMP"/APT_HISTORY
    
    yad --window-icon=/usr/share/icons/mnotify-some-"$(grep IconLook ~/.config/apt-notifierrc | cut -f2 -d=)".png \\
        --width=$(xprop -root | grep _NET_DESKTOP_GEOMETRY\(CARDINAL\) | awk '{print $3*.75}' | cut -f1 -d.) \\
        --height=480 \\
        --center \\
        --title "$AptHistory" \\
        --text-info \\
        --filename="$TMP"/APT_HISTORY \\
        --fontname=mono \\
        --button=gtk-close \\
        --margins=7 \\
        --borders=5
        
    rm -rf "$TMP"    
    
    '''
    script_file = tempfile.NamedTemporaryFile('wt')
    script_file.write(script)
    script_file.flush()
    run = subprocess.Popen(['sh %s' % script_file.name],shell=True).wait()
    script_file.close()
    Check_for_Updates_by_User = 'true'
    check_updates()
    
def apt_get_update():
    global Check_for_Updates_by_User
    
    # ~~~ Localize 4 ~~~

    t01 = _("The action you requested needs <b>root privileges</b>. Please enter <b>root's</b> password below.")
    shellvar = '    rootPasswordRequestMsg="' + t01 + '"\n'
    
    script = '''#! /bin/bash
''' + shellvar + '''

    #for MEPIS remove "MX" branding from the $window_title string
    window_title=$(echo "$window_title"|sed 's/MX /'$(grep -o MX.*[1-9][0-9] /etc/issue|cut -c1-2)" "'/')

    TermXOffset="$(xwininfo -root|awk '/Width/{print $2/4}')"
    TermYOffset="$(xwininfo -root|awk '/Height/{print $2/4}')"
    G=" --geometry=80x25+"$TermXOffset"+"$TermYOffset
    #I=" --icon=mnotify-some-""$(grep IconLook ~/.config/apt-notifierrc | cut -f2 -d=)"
    #T=" --title='""$(grep -o MX.*[1-9][0-9] /etc/issue|cut -c1-2)"" apt-notifier: apt-get update'"
    if (xprop -root | grep -q -i kde)
      then
        # Running KDE
        #
        # Can't get su-to-root to work in newer KDE's, so use kdesu for authentication.
        #  
        # If x-terminal-emulator is set to xfce4-terminal.wrapper, use     
        # xfce4-terminal instead because the --hold option doesn't work with
        # the wrapper. Also need to enclose the apt-get command in single quotes.
        #
        # If x-terminal-emulator is set to gnome-terminal.wrapper, use konsole instead, if it's available (it should be), if not do nothing.
        # If x-terminal-emulator is set to xterm,                  use konsole instead, if it's available (it should be), if not use xterm.

        case $(readlink -e /usr/bin/x-terminal-emulator | xargs basename) in
        
          gnome-terminal.wrapper) if [ -e /usr/bin/konsole ]
                                    then
                                      $(kde4-config --path libexec)kdesu -c "konsole -e apt-get update"
                                      sleep 5
                                    else
                                      :
                                  fi
                                  ;;

                         konsole) $(kde4-config --path libexec)kdesu -c "konsole -e apt-get update"
                                  sleep 5
                                  ;;

                         roxterm) $(kde4-config --path libexec)kdesu -c "roxterm$G$T --separare -e apt-get update"
                                  ;;

          xfce4-terminal.wrapper) $(kde4-config --path libexec)kdesu -c "xfce4-terminal$G$I$T -e 'apt-get update'"
                                  ;;

                           xterm) if [ -e /usr/bin/konsole ]
                                    then
                                      $(kde4-config --path libexec)kdesu -c "konsole -e apt-get update"
                                      sleep 5
                                    else
                                      $(kde4-config --path libexec)kdesu -c "xterm -e apt-get update"
                                  fi
                                  ;;

                               *) $(kde4-config --path libexec)kdesu -c "x-terminal-emulator -e apt-get update"
                                  ;;
        esac

      else
        # Running a non KDE desktop
        # 
        # Use su-to-root for authentication, it should end up using gksu.
        # 
        # If x-terminal-emulator is set to xfce4-terminal.wrapper, use 
        # xfce4-terminal instead because the --hold option doesn't work
        # with the wrapper. Also need to enclose the apt-get command in
        # single quotes.
        #
        # If x-terminal-emulator is set to gnome-terminal.wrapper, use xfce4-terminal instead, if it's available (it is in MX), if not use gnome-terminal.
        # If x-terminal-emulator is set to xterm,                  use xfce4-terminal instead, if it's available (it is in MX), if not use xterm.

        case $(readlink -e /usr/bin/x-terminal-emulator | xargs basename) in

          gnome-terminal.wrapper) su-to-root -X -c "gnome-terminal$G$T -e 'apt-get update'"
                                  ;;

                         konsole) su-to-root -X -c "konsole -e apt-get update"
                                  sleep 5
                                  ;;

                         roxterm) su-to-root -X -c "roxterm$G$T --separate -e apt-get update"
                                  ;;

          xfce4-terminal.wrapper) if [ -x $(whereis gksu | awk '{print $2}') ]
                                    then
                                      gksu --su-mode -m "$rootPasswordRequestMsg""\n\n'apt-get update'" "xfce4-terminal$G$I$T -e 'apt-get update'"
                                    else
                                      su-to-root -X -c "xfce4-terminal$G$I$T -e 'apt-get update"
                                  fi                                      
                                  ;;

                           xterm) if [ -e /usr/bin/xfce4-terminal ]
                                    then
                                      su-to-root -X -c "xfce4-terminal$G$I$T -e 'apt-get update'"
                                    else
                                      su-to-root -X -c "xterm -e apt-get update"
                                  fi
                                  ;;

                               *) su-to-root -X -c "x-terminal-emulator -e apt-get update"
                                  ;;

        esac
    fi
    
    '''
    script_file = tempfile.NamedTemporaryFile('wt')
    script_file.write(script)
    script_file.flush()
    run = subprocess.Popen(['sh %s' % script_file.name],shell=True).wait()
    script_file.close()
    Check_for_Updates_by_User = 'true'
    check_updates()

def re_enable_click():
    global ignoreClick
    ignoreClick = '0'

def start_synaptic0():
    global ignoreClick
    global Timer
    if ignoreClick != '1':
        start_synaptic()    
        ignoreClick = '1'
        Timer.singleShot(50, re_enable_click)
    else:
        pass

def viewandupgrade0():
    global ignoreClick
    global Timer
    if ignoreClick != '1':
        viewandupgrade()    
        ignoreClick = '1'
        Timer.singleShot(50, re_enable_click)
    else:
        pass

# Define the command to run when left clicking on the Tray Icon
def left_click():
    if text.startswith( "0" ):
        start_synaptic0()
    else:
        """Test ~/.config/apt-notifierrc for LeftClickViewAndUpgrade"""
        command_string = "cat " + rc_file_name + " | grep -q LeftClick=ViewAndUpgrade"
        exit_state = subprocess.call([command_string], shell=True, stdout=subprocess.PIPE)
        if exit_state == 0:
            viewandupgrade0()
        else:
            start_synaptic0()

# Define the action when left clicking on Tray Icon
def left_click_activated(reason):
    if reason == QtGui.QSystemTrayIcon.Trigger:
        left_click()

def read_icon_config():
    """Reads ~/.config/apt-notifierrc, returns 'show' if file doesn't exist or does not contain DontShowIcon"""
    command_string = "cat " + rc_file_name + " | grep -q DontShowIcon"
    exit_state = subprocess.call([command_string], shell=True, stdout=subprocess.PIPE)
    if exit_state != 0:
        return "show"

def read_icon_look():
    script = '''#! /bin/bash
    grep IconLook ~/.config/apt-notifierrc | cut -f2 -d=
    '''
    script_file = tempfile.NamedTemporaryFile('wt')
    script_file.write(script)
    script_file.flush()
    run = subprocess.Popen(["echo -n `sh %s`" % script_file.name],shell=True, stdout=subprocess.PIPE)
    # Read the output into a text string
    iconLook = run.stdout.read(128)
    script_file.close()
    return iconLook
    
def set_noicon():
    """Reads ~/.config/apt-notifierrc. If "DontShowIcon blah blah blah" is already there, don't write it again"""
    command_string = "cat " + rc_file_name + " | grep -q DontShowIcon"
    exit_state = subprocess.call([command_string], shell=True, stdout=subprocess.PIPE)
    if exit_state != 0:
        file = open(rc_file_name, 'a')
        file.write ('[DontShowIcon] #Remove this entry if you want the apt-notify icon to show even when there are no upgrades available\n')
        file.close()
        subprocess.call(["/usr/bin/apt-notifier"], shell=True, stdout=subprocess.PIPE)
    AptIcon.hide()
    icon_config = "donot show"

def add_rightclick_actions():
    ActionsMenu.clear()
    """Test ~/.config/apt-notifierrc for LeftClickViewAndUpgrade"""
    command_string = "cat " + rc_file_name + " | grep -q LeftClick=ViewAndUpgrade"
    exit_state = subprocess.call([command_string], shell=True, stdout=subprocess.PIPE)
    if exit_state == 0:
        AptNotify.connect(ActionsMenu.addAction(View_and_Upgrade), QtCore.SIGNAL("triggered()"), viewandupgrade0)
        ActionsMenu.addSeparator()
        AptNotify.connect(ActionsMenu.addAction(Upgrade_using_Synaptic), QtCore.SIGNAL("triggered()"), start_synaptic0)
    else:
        AptNotify.connect(ActionsMenu.addAction(Upgrade_using_Synaptic), QtCore.SIGNAL("triggered()"), start_synaptic0)
        ActionsMenu.addSeparator()
        AptNotify.connect(ActionsMenu.addAction(View_and_Upgrade), QtCore.SIGNAL("triggered()"), viewandupgrade0)        
    add_apt_history_action()        
    add_apt_get_update_action()
    add_apt_notifier_help_action()
    add_synaptic_help_action()
    add_aptnotifier_prefs_action()
    add_quit_action()

def add_hide_action():
    ActionsMenu.clear()
    if icon_config == "show":
        hide_action = ActionsMenu.addAction(Hide_until_updates_available)
        AptNotify.connect(hide_action,QtCore.SIGNAL("triggered()"),set_noicon)
        ActionsMenu.addSeparator()
        AptNotify.connect(ActionsMenu.addAction(u"Synaptic"), QtCore.SIGNAL("triggered()"), start_synaptic0)        
    add_apt_history_action()    
    add_apt_get_update_action()
    add_apt_notifier_help_action()
    add_synaptic_help_action()
    add_aptnotifier_prefs_action()
    add_quit_action()

def add_quit_action():
    ActionsMenu.addSeparator()
    quit_action = ActionsMenu.addAction(QuitIcon,Quit_Apt_Notifier)
    AptNotify.connect(quit_action, QtCore.SIGNAL("triggered()"), exit)

def add_apt_notifier_help_action():
    ActionsMenu.addSeparator()
    apt_notifier_help_action = ActionsMenu.addAction(HelpIcon,Apt_Notifier_Help)
    apt_notifier_help_action.triggered.connect(open_apt_notifier_help)
    
def open_apt_notifier_help():
    """ check if mx-viewer is installed, if it is use it to display help, otherwise use xdg-open """
    command_string = "test -e /usr/bin/mx-viewer"
    exit_state = subprocess.call([command_string], shell=True, stdout=subprocess.PIPE)
    if exit_state == 0:
        subprocess.Popen(['mx-viewer https://mxlinux.org/wiki/help-files/help-mx-apt-notifier'],shell=True)
    else:
        subprocess.Popen(['xdg-open  https://mxlinux.org/wiki/help-files/help-mx-apt-notifier'],shell=True) 

    
def add_synaptic_help_action():
    ActionsMenu.addSeparator()
    synaptic_help_action = ActionsMenu.addAction(HelpIcon,Synaptic_Help)
    synaptic_help_action.triggered.connect(open_synaptic_help)
    
def open_synaptic_help():
    """ check if mx-viewer is installed, if it is use it to display help, otherwise use xdg-open """
    command_string = "test -e /usr/bin/mx-viewer"
    exit_state = subprocess.call([command_string], shell=True, stdout=subprocess.PIPE)
    if exit_state == 0:
        subprocess.Popen(['mx-viewer https://mxlinux.org/user_manual_mx15/mxum.html#toc-Subsection-5.3'],shell=True)
    else:
        subprocess.Popen(['xdg-open  https://mxlinux.org/user_manual_mx15/mxum.html#toc-Subsection-5.3'],shell=True)

def add_aptnotifier_prefs_action():
    ActionsMenu.addSeparator()
    aptnotifier_prefs_action =  ActionsMenu.addAction(Apt_Notifier_Preferences)
    AptNotify.connect(aptnotifier_prefs_action,QtCore.SIGNAL("triggered()"), aptnotifier_prefs)

def add_apt_history_action():
    ActionsMenu.addSeparator()
    apt_history_action =  ActionsMenu.addAction(Apt_History)
    AptNotify.connect(apt_history_action,QtCore.SIGNAL("triggered()"), apt_history)

def add_apt_get_update_action():
    ActionsMenu.addSeparator()
    apt_get_update_action =  ActionsMenu.addAction(Check_for_Updates)
    AptNotify.connect(apt_get_update_action,QtCore.SIGNAL("triggered()"), apt_get_update)

# General application code	
def main():
    # Define Core objects, Tray icon and QTimer 
    global AptNotify
    global AptIcon
    global QuitIcon
    global icon_config
    global quit_action    
    global Timer
    global initialize_aptnotifier_prefs
    global read_icon_look
    global icon_set
    
    set_translations()
    initialize_aptnotifier_prefs()
    AptNotify = QtGui.QApplication(sys.argv)
    AptIcon = QtGui.QSystemTrayIcon()
    Timer = QtCore.QTimer()
    icon_config = read_icon_config()
    # Define the icons:
    global NoUpdatesIcon
    global NewUpdatesIcon
    global HelpIcon
    
    # read in icon look into a variable
    icon_set = read_icon_look()
    
    NoUpdatesIcon = QtGui.QIcon("/usr/share/icons/mnotify-none-" + icon_set + ".png")
    NewUpdatesIcon  = QtGui.QIcon("/usr/share/icons/mnotify-some-" + icon_set + ".png")
    HelpIcon = QtGui.QIcon("/usr/share/icons/oxygen/22x22/apps/help-browser.png")
    QuitIcon = QtGui.QIcon("/usr/share/icons/oxygen/22x22/actions/system-shutdown.png")
    # Create the right-click menu and add the Tooltip text
    global ActionsMenu
    ActionsMenu = QtGui.QMenu()
    AptIcon.connect( AptIcon, QtCore.SIGNAL( "activated(QSystemTrayIcon::ActivationReason)" ), left_click_activated)
    AptNotify.connect(Timer, QtCore.SIGNAL("timeout()"), check_updates)
    # Integrate it together,apply checking of updated packages and set timer to every 1 minute(s) (1 second = 1000)
    AptIcon.setIcon(NoUpdatesIcon)
    AptIcon.setContextMenu(ActionsMenu)
    if icon_config == "show":
        AptIcon.show()
    check_updates()
    Timer.start(60000)
    if AptNotify.isSessionRestored():
        sys.exit(1)
    sys.exit(AptNotify.exec_())

if __name__ == '__main__':
    main()
