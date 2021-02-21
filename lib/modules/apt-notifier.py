#! /usr/bin/python3
# -*- coding: utf-8 -*-

import subprocess
import sys
MODULES = "/usr/lib/apt-notifier/modules"

if MODULES not in sys.path:
    sys.path.append(MODULES)

import os
import dbus
import tempfile
from os import environ

from PyQt5 import QtWidgets, QtGui
from PyQt5 import QtCore

from distutils import spawn
from time import sleep
from string import Template # for simple string substitution (popup_msg...)



def fix_fluxbox_startup():
    cmd  = "[ -f  ~/.fluxbox/startup ]"
    cmd += " && sed -i -r -e '\![[:space:]]*(/usr/bin/)?python[23]?[[:space:]]+(/usr/bin/)?apt-notifier.py.*!s![[:space:]]*(/usr/bin/)?python[23]?[[:space:]]+! !' ~/.fluxbox/startup;"
    run = subprocess.run(cmd, shell=True, executable="/bin/bash")


def set_package_manager():
    global package_manager
    global package_manager_enabled
    global package_manager_name
    global package_manager_exec
    global package_manager_path
    global show_package_manager
    global show_package_manager_help
    global package_manager_available
    try: 
        show_package_manager
    except:
        show_package_manager = False

    try: package_manager_path
    except:
         package_manager_path = ''
    
    #if show_package_manager and package_manager_path:
    #    return
    global conf
    try: conf
    except NameError:
        from aptnotifier_config import AptNotifierConfig
        conf = AptNotifierConfig()
    
    # allowed package manger
    default_list =  "synaptic, muon"
    default_list =  default_list.replace(',', ' ').split()
    # get list from config settings
    preference_list = conf.get('package_manager_preference_list')
    preference_list = preference_list.replace(',', ' ').split()
    # accept only default_list entries
    check_list = [ x.lower() for x in preference_list if x in default_list ]

    from shutil import which

    # check available and preferred package manager
    for pm in check_list:
        if pm == 'synaptic':
            show_package_manager = conf.config['show_synaptic']
            show_package_manager_help = conf.get('show_synaptic_help')
            debug_p(f"find package_manager: {pm}")
            path = which("synaptic-pkexec")
            if path:
                package_manager = "synaptic"
                package_manager_exec = "synaptic-pkexec"
                package_manager_name = "Synaptic"
                package_manager_path = path
                package_manager_available = True
                package_manager_enabled = True
                debug_p(f"found package_manager: {package_manager_exec}")
                break
            
            path = which("synaptic")
            if path:
                package_manager = "synaptic"
                package_manager_exec = "su-to-root -X -c synaptic"
                package_manager_name = "Synaptic"
                package_manager_path = path
                package_manager_available = True
                package_manager_enabled = True
                debug_p(f"found package_manager: {package_manager_exec}")
                break
            else:
                package_manager = ""
                package_manager_exec = ""
                package_manager_name = ""
                package_manager_path = ''
                package_manager_available = False
                package_manager_enabled = False
                debug_p(f"no package_manager found: {pm}")
                    
        if pm == 'muon':
            show_package_manager = conf.config['show_muon']
            show_package_manager_help = conf.get('show_muon_help')
            path = which(pm)
            if path:
                package_manager = "muon"
                package_manager_name = "Muon"
                package_manager_path = path
                package_manager_available = True
                package_manager_enabled = True
                path_pk = which("muon-pkexec")
                if path_pk:
                    package_manager_exec = "muon-pkexec"
                    package_manager_path = path_pk
                elif  which("mx-pkexec"):
                    package_manager_exec = f"mx-pkexec {path}"
                else:
                    package_manager_exec = "su-to-root -X -c muon"
            else:
                package_manager_available = False
                package_manager = ""
                package_manager_exec = ""
                package_manager_name = ""
                package_manager_path = ""
                package_manager_enabled = False

    if not package_manager:
        package_manager_available = False
        package_manager_enabled = False
        show_package_manager = False
        show_package_manager_help = False
        print("Info: No package manager found! Disable packagemanager actions")


def set_globals():
    global Updater_Name
    global Package_Installer
    global tooltip_0_updates_available
    global tooltip_1_new_update_available
    global tooltip_multiple_new_updates_available
    global popup_title
    global popup_msg_1_new_update_available
    global popup_msg_multiple_new_updates_available
    global Upgrade_using_package_manager
    global View_and_Upgrade
    global Hide_until_updates_available
    global Quit_Apt_Notifier
    global Apt_Notifier_Help
    global Package_Manager_Help
    global Apt_Notifier_Preferences
    global Apt_History
    global Apt_History
    global View_Auto_Updates_Logs
    global View_Auto_Updates_Dpkg_Logs
    global Check_for_Updates
    global Force_Check_Counter
    Force_Check_Counter = 0
    global About
    global Check_for_Updates_by_User
    Check_for_Updates_by_User = 'false'
    global ignoreClick
    ignoreClick = '0'
    global WatchedFilesAndDirsHashNow
    WatchedFilesAndDirsHashNow = ''
    global WatchedFilesAndDirsHashPrevious
    WatchedFilesAndDirsHashPrevious = ''
    global AvailableUpdates
    AvailableUpdates = ''
    global Reload
    global notification
    notification = None

    # check version_at_start
    global version_at_start
    version_at_start = version_installed()
    global rc_file_name
    rc_file_name = os.getenv('HOME') + '/.config/apt-notifierrc'

    global message_status
    message_status = "not displayed"
    global notification_icon
    notification_icon = "apt-notifier"


###

    global xlate
    try: xlate
    except NameError:
        from aptnotifier_xlate import AptNotifierXlate
        xlate = AptNotifierXlate()

    Updater_Name                                  = xlate.get('updater_name')
    Apt_Notifier_Help                           = xlate.get('apt_notifier_help')
    Package_Installer                           = xlate.get('mx_package_installer')
    tooltip_0_updates_available                 = xlate.get('tooltip_0_updates_available')
    tooltip_0_updates_available                 = xlate.get('tooltip_0_updates_available')
    tooltip_1_new_update_available              = xlate.get('tooltip_1_new_update_available')
    tooltip_multiple_new_updates_available      = xlate.get('tooltip_multiple_new_updates_available')
    popup_title                                 = xlate.get('popup_title')
    popup_msg_1_new_update_available            = xlate.get('popup_msg_1_new_update_available')
    popup_msg_multiple_new_updates_available    = xlate.get('popup_msg_multiple_new_updates_available')
    Upgrade_using_package_manager               = xlate.get('upgrade_using_package_manager')
    View_and_Upgrade                            = xlate.get("View and Upgrade")
    Hide_until_updates_available                = xlate.get("Hide until updates available")
    Quit_Apt_Notifier                           = xlate.get("Quit")
    Apt_Notifier_Preferences                    = xlate.get("apt_notifier_preferences")
    Apt_History                                 = xlate.get("apt_history")
    View_Auto_Updates_Logs                      = xlate.get("view_auto_updates_logs")
    View_Auto_Updates_Dpkg_Logs                 = xlate.get("view_auto_updates_dpkg_logs")
    Check_for_Updates                           = xlate.get("check_for_updates")
    About                                       = xlate.get("about")
    Reload                                      = xlate.get("reload")
    left_click_package_manager                  = xlate.get('left_click_package_manager')
    
    global package_manager_name
    if package_manager_name:
        xlate.left_click_package_manager = package_manager_name
    
    global package_manager_enabled
    set_package_manager()
    if package_manager_enabled:
        Package_Manager_Help = xlate.get('package_manager_help')
        Package_Manager_Help = Package_Manager_Help.replace("Synaptic", package_manager_name)
        Upgrade_using_package_manager = Upgrade_using_package_manager.replace('Synaptic', package_manager_name)

    global show_package_manager_help
    if show_package_manager_help:
        Package_Manager_Help = xlate.get('package_manager_help')
        Package_Manager_Help = Package_Manager_Help.replace("Synaptic", package_manager_name)
        Upgrade_using_package_manager = Upgrade_using_package_manager.replace('Synaptic', package_manager_name)

    global conf
    try: conf
    except NameError:
        from aptnotifier_config import AptNotifierConfig
        conf = AptNotifierConfig()
    global show_apt_notifier_help
    show_apt_notifier_help = conf.get('show_apt_notifier_help')

    global apt_notifier_rc
    try: apt_notifier_rc
    except NameError:
        from aptnotifier_rc import AptNotifierRC
        apt_notifier_rc = AptNotifierRC()

    # UseNotifier
    global UseNotifier
    global use_dbus_notifications

    debug_p("set_globals():  if conf.get('use_dbus_notifications') == True:")
    debug_p(f"set_globals(): if {conf.get('use_dbus_notifications')} == True:")

    if conf.get('use_dbus_notifications') == True:
        use_dbus_notifications = True
        UseNotifier = 'dbus'
    else:
        use_dbus_notifications = False
        UseNotifier = 'qt'

    debug_p("set_globals(): if apt_notifier_rc.use_dbus_notifications == True:")
    debug_p(f"set_globals():if {apt_notifier_rc.use_dbus_notifications} == True:")
    if apt_notifier_rc.use_dbus_notifications == True:
        UseNotifier = 'dbus'
        use_dbus_notifications = True
    elif apt_notifier_rc.use_dbus_notifications == False:
        UseNotifier = 'qt'
        use_dbus_notifications = False
    debug_p(f"set_globals(): UseNotifier: {UseNotifier}")
    debug_p(f"set_globals(): use_dbus_notifications: {use_dbus_notifications}")


# Check for updates, using subprocess.Popen
def check_updates():
    global message_status
    global AvailableUpdates
    global WatchedFilesAndDirsHashNow
    global WatchedFilesAndDirsHashPrevious
    global Check_for_Updates_by_User
    global Force_Check_Counter

    debug_p("check_updates")

    """
    Don't bother checking for updates when /var/lib/apt/periodic/update-stamp
    isn't present. This should only happen in a Live session before the repository
    lists have been loaded for the first time.
    """
    update_stamp = os.path.isfile('/var/lib/apt/periodic/update-stamp')
    lock = os.path.isfile('/var/lib/apt/lists/lock')
    if not update_stamp and not lock:
        if AvailableUpdates == "":
            AvailableUpdates = "0"
        if AvailableUpdates == "0":
            message_status = "not displayed"  # Resets flag once there are no more updates
            add_hide_action()
        if icon_config != "show":
            AptIcon.hide()
        else:
            AptIcon.setIcon(NoUpdatesIcon)
            if unattended_upgrade_enabled():
                AptIcon.setToolTip("")
            else:
                AptIcon.setToolTip(tooltip_0_updates_available)
        return

    """
    Don't bother checking for updates if processes for other package management tools
    appear to be runninng. For unattended-upgrade, use '/usr/bin/unattended-upgrade'
    to avoid getting a hit on /usr/share/unattended-upgrades/unattended-upgrade-shutdown
    which appears to be started automatically when using systemd as init.
    """
    cmd = "sudo lsof "
    cmd+= "/var/lib/dpkg/lock "
    cmd+= "/var/lib/dpkg/lock-frontend "
    cmd+= "/var/lib/apt/lists/lock "
    cmd+= "/var/cache/apt/archives/lock "
    cmd+= "2>/dev/null "
    cmd+= "| grep -qE 'lock$|lock-frontend$'"
    ret = subprocess.run(cmd, shell=True).returncode
    if ret == 0:
        Force_Check_Counter = 5
        return

    """
    Get a hash of files and directories we are watching
    """
    script = '''#!/bin/bash
    WatchedFilesAndDirs=(
    /etc/apt/apt.conf*
    /etc/apt/preferences*
    /var/lib/apt*
    /var/lib/apt/lists
    /var/lib/apt/lists/partial
    /var/lib/dpkg
    /var/cache/apt
    /var/lib/synaptic/preferences
    )
    stat -c %Y,%Z ${WatchedFilesAndDirs[*]} 2>/dev/null | md5sum
    '''
    #cmd = script
    #run = subprocess.run(cmd, capture_output=True, shell=True, text=True, executable="/bin/bash")
    #WatchedFilesAndDirsHashNow = run.stdout.strip()
    WatchedFilesAndDirsHashNow = get_stat_hash_of_watched_files_and_dirs()
    """
    If
        no changes in hash of files and directories being watched since last checked
            AND
        the call to check_updates wasn't initiated by user
    then don't bother checking for updates.
    """
    debug_p(f"Hash: {WatchedFilesAndDirsHashNow} == {WatchedFilesAndDirsHashPrevious}")
    if WatchedFilesAndDirsHashNow == WatchedFilesAndDirsHashPrevious:
        if Check_for_Updates_by_User == 'false':
            if Force_Check_Counter < 5:
                Force_Check_Counter = Force_Check_Counter + 1
                if AvailableUpdates == '':
                    AvailableUpdates = '0'
                return

    WatchedFilesAndDirsHashPrevious = WatchedFilesAndDirsHashNow
    WatchedFilesAndDirsHashNow = ''

    Force_Check_Counter = 1

    Check_for_Updates_by_User = 'false'
    global apt
    try: apt
    except NameError:
        from aptnotifier_apt import Apt
        apt = Apt()
    AvailableUpdates = apt.available_updates()
    debug_p(f"check_updates AvailableUpdates {AvailableUpdates}")

    # Alter both Icon and Tooltip, depending on updates available or not
    if AvailableUpdates == "":
        AvailableUpdates = "0"
    if AvailableUpdates == "0":
        message_status = "not displayed"  # Resets flag once there are no more updates
        add_hide_action()
        if icon_config != "show":
            AptIcon.hide()
        else:
            AptIcon.setIcon(NoUpdatesIcon)
            if unattended_upgrade_enabled():
                AptIcon.setToolTip("")
            else:
                AptIcon.setToolTip(tooltip_0_updates_available)
    else:
        if AvailableUpdates == "1":
            AptIcon.setIcon(NewUpdatesIcon)
            AptIcon.show()
            AptIcon.setToolTip(tooltip_1_new_update_available)
            add_rightclick_actions()
            # Shows the pop up message only if not displayed before
            if message_status == "not displayed":
                cmd = "for WID in $(wmctrl -l | cut -d' ' -f1); do xprop -id $WID | grep 'NET_WM_STATE(ATOM)'; done | grep -sq _NET_WM_STATE_FULLSCREEN"
                run = subprocess.run(cmd, shell=True)
                if run.returncode == 1:
                    show_popup(popup_title, popup_msg_1_new_update_available, notification_icon)
                    message_status = "displayed"
                """
                    UseNotifier = use_notifier()
                    #print( "UseNotifier:" + UseNotifier)
                    if UseNotifier.startswith("qt"):
                        def show_message():
                            AptIcon.showMessage(popup_title, popup_msg_1_new_update_available)
                        Timer.singleShot(1000, show_message)
                    else:
                        desktop_notification(popup_title, popup_msg_1_new_update_available, notification_icon)
                """
        else:
            AptIcon.setIcon(NewUpdatesIcon)
            AptIcon.show()
            tooltip_template=Template(tooltip_multiple_new_updates_available)
            tooltip_with_count=tooltip_template.substitute(count=AvailableUpdates)
            AptIcon.setToolTip(tooltip_with_count)
            
            add_rightclick_actions()
            # Shows the pop up message only if not displayed before
            if message_status == "not displayed":
                cmd = "for WID in $(wmctrl -l | cut -d' ' -f1); do xprop -id $WID | grep 'NET_WM_STATE(ATOM)'; done | grep -sq _NET_WM_STATE_FULLSCREEN"
                run = subprocess.run(cmd, shell=True)
                if run.returncode == 1:
                    # ~~~ Localize 1b ~~~
                    # Use embedded count placeholder.
                    popup_template=Template(popup_msg_multiple_new_updates_available)
                    popup_with_count=popup_template.substitute(count=AvailableUpdates)
                    show_popup(popup_title, popup_with_count, notification_icon)
                    message_status = "displayed"


def run_with_restart(prog_exec=None):
    global AptIcon
    global Timer
    global version_at_start
    from subprocess import run, DEVNULL, Popen
    from time import sleep
    if not prog_exec:
        return False
    ret =''
    if run_in_plasma():
        restart = "ionice -c3 nice -n19 /usr/bin/python3 /usr/lib/apt-notifier/modules/apt-notifier.py & disown -h"
        cmd = prog_exec + ';' + restart
        run = Popen(cmd, shell=True, executable="/bin/bash")
        AptIcon.hide()
        from time import sleep
        sleep(1);
        sys.exit(0)
    else:
        cmd = "sudo -k"
        run(cmd.split())
        cmd = prog_exec
        ret = run(cmd.split()).returncode
    if  version_at_start != version_installed():
        restart_apt_notifier()
    return ret
    
def start_package_manager():
    global Check_for_Updates_by_User
    global package_manager_available
    global version_at_start
    
    debug_p(f"run_with_restart({package_manager_exec})")
    if not package_manager_available:
        return

    ret = run_with_restart(package_manager_exec)
   
    if ret == 0:
        Check_for_Updates_by_User = 'true'
        debug_p("check_updates()")
        check_updates()

def start_package_managerXXXX():
    global Check_for_Updates_by_User
    global package_manager_available
    if not package_manager_available:
        return
    from subprocess import run
    cmd = "pgrep -x plasmashell >/dev/null && exit 1 || exit 0"
    running_in_plasma = subprocess.run(cmd, shell=True).returncode
    if  running_in_plasma:
        systray_icon_hide()
        #cmd = package_manager_exec + "; ionice -c3 nice -n19 /usr/bin/apt-notifier.py & disown -h;"
        cmd = package_manager_exec
        ret = run(cmd.split()).returncode
        systray_icon_show()
    else:
        cmd = "sudo -k"
        run(cmd.split())
        cmd = package_manager_exec
        ret = run(cmd.split()).returncode

    debug_p(f"run(cmd.split()) = run({cmd.split()})")
    debug_p(f"run(cmd.split()).returncode= {ret}")
    cmd = "dpkg-query -f ${Version} -W apt-notifier"
    version_installed = run(cmd.split(), capture_output=True, text=True).stdout.strip()
    if  version_installed != version_at_start:
        cmd = "apt-notifier-unhide-Icon & disown -h >/dev/null 2>/dev/null"
        run(cmd, shell=True, executable="/bin/bash")
        sleep(2)

    if ret == 0:
        Check_for_Updates_by_User = 'true'
        debug_p("check_updates()")
        check_updates()


def start_viewandupgrade(action=None):
    notification_close()
    global Check_for_Updates_by_User
    systray_icon_hide()
    initialize_aptnotifier_prefs()

    from subprocess import run, PIPE
    global conf
    try: conf
    except NameError:
        from aptnotifier_config import AptNotifierConfig
        conf = AptNotifierConfig()

    global apt_notifier_rc
    try: apt_notifier_rc
    except NameError:
        from aptnotifier_rc import AptNotifierRC
        apt_notifier_rc = AptNotifierRC()

    global view_and_upgrade
    try: view_and_upgrade
    except NameError:
        from aptnotifier_viewandupgrade import ViewAndUpgrade
        view_and_upgrade = ViewAndUpgrade()

    systray_icon_hide()
    while True:
        view_and_upgrade.yad
        returncode = view_and_upgrade.yad_returncode
        if returncode not in [ 0, 8]:
            break
        else:
            apt_notifier_rc.upgrade_assume_yes = view_and_upgrade.upgrade_assume_yes
            apt_notifier_rc.upgrade_auto_close = view_and_upgrade.upgrade_auto_close
            apt_notifier_rc.update

        # reload
        if returncode == 8:
            run('/usr/lib/apt-notifier/bin/updater_reload_run')
            view_and_upgrade.apt_list_run

        # upgrade
        if returncode == 0:

            cmd = '/usr/lib/apt-notifier/bin/updater_upgrade_run'
            """
            pmd = "pgrep -x plasmashell >/dev/null && exit 1 || exit 0"
            running_in_plasma = subprocess.run(pmd, shell=True).returncode
            if  running_in_plasma: # and action is None:
                cmd = "( /usr/lib/apt-notifier/bin/updater_upgrade_run; apt-notifier-unhide-Icon; )& disown -h >/dev/null 2>/dev/null"
                subprocess.Popen(cmd, shell=True, executable="/bin/bash")
                AptIcon.hide()
                sleep(2)
                sys.exit(1)
            else:
            """
            run(cmd)
            cmd = "dpkg-query -f ${Version} -W apt-notifier"
            version_installed = subprocess.run(cmd.split(), capture_output=True, universal_newlines=True).stdout.strip()
            if  version_installed != version_at_start:
                cmd = "apt-notifier-unhide-Icon & disown -h >/dev/null 2>/dev/null"
                run = subprocess.run(cmd, shell=True, executable="/bin/bash")
                sleep(1)
                sys.exit(0)

            break

        Check_for_Updates_by_User = 'true'
    systray_icon_show()
    check_updates()

def initialize_aptnotifier_prefs():

    """Create/initialize preferences in the ~/.config/apt-notifierrc file  """
    """if they don't already exist. Remove multiple entries and those that """
    """appear to be invalid.                                               """
    global conf
    global icon_look
    global wireframe_transparent
    global tray_icon_noupdates
    global tray_icon_newupdates
    global use_dbus_notifications
    global window_icon
    global window_icon_kde

    from aptnotifier_rc import AptNotifierRC

    global apt_notifier_rc
    try: apt_notifier_rc
    except NameError:
        apt_notifier_rc = AptNotifierRC()

    try: conf
    except NameError:
        from aptnotifier_config import AptNotifierConfig
        conf = AptNotifierConfig()

    icon_look = apt_notifier_rc.icon_look
    wireframe_transparent = apt_notifier_rc.wireframe_transparent

    window_icon = conf.config['window_icon']
    window_icon_kde = conf.config['window_icon_kde']

    if icon_look == 'classic':
        tray_icon_newupdates = conf.config['classic_some']
        tray_icon_noupdates  = conf.config['classic_none']
    elif icon_look == 'pulse':
        tray_icon_newupdates = conf.config['pulse_some']
        tray_icon_noupdates  = conf.config['pulse_none']
    elif icon_look == 'wireframe-dark':
        tray_icon_newupdates = conf.config['wireframe_some']
        if  wireframe_transparent:
            tray_icon_noupdates = conf.config['wireframe_none_dark_transparent']
        else:
            tray_icon_noupdates = conf.config['wireframe_none_dark']
    elif icon_look == 'wireframe-light':
        tray_icon_newupdates = conf.config['wireframe_some']
        if  wireframe_transparent:
            tray_icon_noupdates = conf.config['wireframe_none_light_transparent']
        else:
            tray_icon_noupdates = conf.config['wireframe_none_light']
    else:
        # fallback
        tray_icon_newupdates = conf.config['wireframe_some']
        tray_icon_noupdates = conf.config['wireframe_none_dark']

def aptnotifier_prefs():
    notification_close()

    global Check_for_Updates_by_User
    global package_manager
    
    systray_icon_hide()

    initialize_aptnotifier_prefs()
    global use_dbus_notifications
    debug_p(f"*** use_dbus_notifications={use_dbus_notifications}")

    sys.path.append("/usr/lib/apt-notifier/modules")
    from aptnotifier_autostart import AutoStart
    from aptnotifier_autoupdate import UnattendedUpgrade
    from aptnotifier_form import Form
    from aptnotifier_rc import AptNotifierRC


    start = AutoStart()
    debug_p(f"form = Form() : {package_manager}")
    
    form = Form()

    if not package_manager_available:
        form.show_left_click_behaviour_frame = False

    form.left_click_package_manager = package_manager
    
    global apt_notifier_rc
    try:
        apt_notifier_rc
    except NameError:
        apt_notifier_rc = AptNotifierRC()

    global autoupdate
    try:
        autoupdate
    except NameError:
        autoupdate = UnattendedUpgrade()

    global conf
    try:
        conf
    except NameError:
        from aptnotifier_config import AptNotifierConfig
        conf = AptNotifierConfig()

    conf_use_dbus_notifications  = conf.get('use_dbus_notifications')
    rc_use_dbus_notifications    = apt_notifier_rc.use_dbus_notifications
    show_switch_desktop_notifications = conf.get('show_switch_desktop_notifications')

    if show_switch_desktop_notifications:
        if rc_use_dbus_notifications in [ True, False ]:
            form.use_dbus_notifications = rc_use_dbus_notifications
            form_use_dbus_notifications = rc_use_dbus_notifications
        else:
            form.use_dbus_notifications = conf_use_dbus_notifications
            form_use_dbus_notifications = conf_use_dbus_notifications

    form.icon_look                = apt_notifier_rc.icon_look
    form.left_click               = apt_notifier_rc.left_click
    form.upgrade_assume_yes       = apt_notifier_rc.upgrade_assume_yes
    form.upgrade_auto_close       = apt_notifier_rc.upgrade_auto_close
    form.upgrade_type             = apt_notifier_rc.upgrade_type
    form.wireframe_transparent    = apt_notifier_rc.wireframe_transparent

    form.autostart                = start.autostart
    form.autoupdate               = autoupdate.unattended_upgrade

    debug_p("form.use_dbus_notifications   = apt_notifier_rc.use_dbus_notifications")
    debug_p(f"{form.use_dbus_notifications}   = {apt_notifier_rc.use_dbus_notifications}")

    form.fill_form()

    debug_p("form.form_token")
    debug_p(f"{form.form_token}")
    debug_p(f"{form.form}")

    form.dialog()

    apt_notifier_rc.icon_look                = form.icon_look
    apt_notifier_rc.left_click               = form.left_click
    apt_notifier_rc.upgrade_assume_yes       = form.upgrade_assume_yes
    apt_notifier_rc.upgrade_auto_close       = form.upgrade_auto_close
    apt_notifier_rc.upgrade_type             = form.upgrade_type
    apt_notifier_rc.wireframe_transparent    = form.wireframe_transparent
    debug_p("form.use_dbus_notifications   = apt_notifier_rc.use_dbus_notifications")
    debug_p(f"{form.use_dbus_notifications}   = {apt_notifier_rc.use_dbus_notifications}")

    debug_p("form.use_dbus_notifications   = apt_notifier_rc.use_dbus_notifications")
    debug_p(f"{form.use_dbus_notifications}   = {apt_notifier_rc.use_dbus_notifications}")

    if show_switch_desktop_notifications:
        if form.use_dbus_notifications in [ True, False ]:
            if not form.use_dbus_notifications == form_use_dbus_notifications:
                apt_notifier_rc.use_dbus_notifications = form.use_dbus_notifications

    apt_notifier_rc.update

    start.autostart  = form.autostart
    autoupdate.autoupdate = form.autoupdate

    global icon_look
    global wireframe_transparent

    icon_look = apt_notifier_rc.icon_look
    wireframe_transparent = apt_notifier_rc.wireframe_transparent

    global tray_icon_noupdates
    global tray_icon_newupdates

    if icon_look == "classic":
        tray_icon_newupdates =  conf.get('classic_some')
        tray_icon_noupdates  =  conf.get('classic_none')
    elif icon_look == "pulse":
        tray_icon_newupdates =  conf.get('pulse_some')
        tray_icon_noupdates  =  conf.get('pulse_none')
    elif icon_look == "wireframe-light":
        tray_icon_newupdates =  conf.get('wireframe_some')
        if wireframe_transparent:
            tray_icon_noupdates  = conf.get('wireframe_none_light_transparent')
        else:
            tray_icon_noupdates  = conf.get('wireframe_none_light')
    else:
        #icon_look == "wireframe-dark":
        tray_icon_newupdates =  conf.get('wireframe_some')
        if wireframe_transparent:
            tray_icon_noupdates  = conf.get('wireframe_none_dark_transparent')
        else:
            tray_icon_noupdates  = conf.get('wireframe_none_dark')
    
    set_QIcons()

    global AptIcon
    global AvailableUpdates
    global NoUpdatesIcon
    if AvailableUpdates == "0":
        AptIcon.setIcon(NoUpdatesIcon)
    else:
        AptIcon.setIcon(NewUpdatesIcon)
    AptIcon.show()
    add_rightclick_actions()

    Check_for_Updates_by_User = 'true'
    systray_icon_show()


def apt_history():
    notification_close()
    systray_icon_hide()
    global apt
    try: apt
    except NameError:
        from aptnotifier_apt import Apt
        apt = Apt()
  
    apt.apt_history()
    
    systray_icon_show()

def apt_get_update():
    notification_close()
    global Check_for_Updates_by_User
    systray_icon_hide()

    run = subprocess.run([ "/usr/lib/apt-notifier/bin/updater_reload_run" ])

    Check_for_Updates_by_User = 'true'
    systray_icon_show()
    check_updates()

def start_package_installer():
    global Check_for_Updates_by_User
    global version_at_start
    systray_icon_hide()

    # find usable package installer
    pl = "mx-packageinstaller packageinstaller"
    from shutil import which
    package_installer = list(filter( lambda x: which(x), pl.split()))[0]
    if not package_installer:
        return
    cmd = f"su-to-root -X -c {package_installer}"
    debug_p(f"start_package_installer(): {cmd}")
    ret = run_with_restart(cmd)
    debug_p(f"start_package_installer(): run_with_restart{cmd}: {ret}")
    
    if  version_at_start != version_installed():
        restart_apt_notifier()
        sleep(2)
   
    if ret == 0:
        Check_for_Updates_by_User = 'true'
        debug_p("check_updates()")
        check_updates()
    systray_icon_show()


def start_package_installerXXX():
    global Check_for_Updates_by_User
    systray_icon_hide()

    # find usable package installer
    pl = "mx-packageinstaller packageinstaller"
    from shutil import which
    package_installer = list(filter( lambda x: which(x), pl.split()))[0]
    if not package_installer:
        return

    # run package installer
    cmd = f"su-to-root -X -c {package_installer}"
    run = subprocess.run(cmd.split())
    # check a newer version of apt-notifier was just installed
    # and restart newer version
    cmd = "dpkg-query -f ${Version} -W apt-notifier"
    version_installed = subprocess.run(cmd.split(), capture_output=True, universal_newlines=True).stdout.strip()
    if  version_installed != version_at_start:
        cmd = "apt-notifier-unhide-Icon & disown -h >/dev/null 2>/dev/null"
        run = subprocess.run(cmd, shell=True, executable="/bin/bash")
        sleep(2)

    Check_for_Updates_by_User = 'true'
    systray_icon_show()
    check_updates()


def re_enable_click():
    global ignoreClick
    ignoreClick = '0'

def start_package_manager0():
    notification_close()
    global ignoreClick
    global Timer
    if ignoreClick != '1':
        start_package_manager()
        ignoreClick = '1'
        Timer.singleShot(50, re_enable_click)
    else:
        pass

def start_viewandupgrade0():
    notification_close()
    global ignoreClick
    global Timer
    if ignoreClick != '1':
        start_viewandupgrade()
        ignoreClick = '1'
        Timer.singleShot(50, re_enable_click)
    else:
        pass

def start_package_installer_0():
    notification_close()
    global ignoreClick
    global Timer
    if ignoreClick != '1':
        start_package_installer()
        ignoreClick = '1'
        Timer.singleShot(50, re_enable_click)
    else:
        pass

# Define the command to run when left clicking on the Tray Icon
def left_click():
    if AvailableUpdates == "0":
        start_package_manager0()
    else:
        """Test ~/.config/apt-notifierrc for LeftClickViewAndUpgrade"""
        cmd = "grep -sq ^LeftClick=ViewAndUpgrade"
        cmd = cmd.split() + [rc_file_name]
        ret = subprocess.run(cmd).returncode
        if ret == 0:
            start_viewandupgrade0()
        else:
            start_package_manager0()

# Define the action when left clicking on Tray Icon
def left_click_activated(reason):
    if reason == QtWidgets.QSystemTrayIcon.Trigger:
        left_click()

def read_icon_config():
    """Reads ~/.config/apt-notifierrc, returns 'show' if file doesn't exist or does not contain DontShowIcon"""
    cmd = "grep -sq ^[[]DontShowIcon[]]"
    cmd = cmd.split() + [rc_file_name]
    ret = subprocess.run(cmd).returncode
    if ret != 0:
        return "show"

def read_icon_look():
    cmd = "grep -m1 -soP ^IconLook=\K.*"
    cmd = cmd.split() + [rc_file_name]
    run = subprocess.run(cmd, capture_output=True, universal_newlines=True)
    iconLook = run.stdout.strip()
    return iconLook

def set_noicon():
    """Inserts a '[DontShowIcon]' line into  ~/.config/apt-notifierrc."""
    cmd = "sed -i -e '1i[DontShowIcon] "
    cmd+= "#Remove this entry if you want the apt-notify icon to show "
    cmd+= "even when there are no upgrades available' "
    cmd+= "-e '/DontShowIcon/d' "

    cmd = ['sed', '-i', '-e',
        '1i[DontShowIcon] #Remove this entry if you want the apt-notify icon to show even when there are no upgrades available',
        '-e', '/DontShowIcon/d', rc_file_name]
    run = subprocess.run(cmd)
    AptIcon.hide()
    icon_config = "donot show"

def add_rightclick_actions():
    global show_package_manager
    global package_manager_enabled
    global show_package_manager_help
    global package_manager_path
    global rc_file_name
    
    from shutil import which
    from subprocess import run, DEVNULL

    set_package_manager()

    ActionsMenu.clear()
    debug_p(f"add_rightclick_actions with {package_manager_path}")
    cmd = f"grep -sq ^LeftClick=ViewAndUpgrade {rc_file_name}" 
    cmd = cmd.split() 
    ret = run(cmd, stdout=DEVNULL, stderr=DEVNULL).returncode
    if ret == 0:
        ActionsMenu.addAction(View_and_Upgrade).triggered.connect( start_viewandupgrade0 )
        if show_package_manager and package_manager_enabled:
            if package_manager_path:
                ActionsMenu.addSeparator()
                ActionsMenu.addAction(Upgrade_using_package_manager).triggered.connect( start_package_manager0 )
    else:
        if show_package_manager and package_manager_enabled:
            if package_manager_path:
                ActionsMenu.addAction(Upgrade_using_package_manager).triggered.connect( start_package_manager0)
                ActionsMenu.addSeparator()
        ActionsMenu.addAction(View_and_Upgrade).triggered.connect( start_viewandupgrade0 )
    
    # check we have a package installer
    pl = "mx-packageinstaller packageinstaller"
    
    package_installer = list(filter( lambda x: which(x), pl.split()))[0]
    if package_installer:
        add_Package_Installer_action()

    add_apt_history_action()

    if unattended_upgrade_enabled():
       add_view_unattended_upgrades_logs_action()
       add_view_unattended_upgrades_dpkg_logs_action()

    add_apt_get_update_action()
    add_apt_notifier_help_action()
    
    if show_package_manager_help and package_manager_enabled:
        if package_manager_path:
            add_package_manager_help_action()
    
    add_aptnotifier_prefs_action()
    add_about_action()
    add_quit_action()

    cmd = '[ "$XDG_CURRENT_DESKTOP" = "XFCE" ] && '
    cmd+= 'which deartifact-xfce-systray-icons && '
    cmd+= 'deartifact-xfce-systray-icons 1 &'
    subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def add_hide_action():
    global show_package_manager
    global package_manager_enabled
    global show_package_manager_help
    global package_manager_path
    from shutil import which
    if package_manager_path:
        if not which(package_manager_path):
            set_package_manager()

    ActionsMenu.clear()
    if icon_config == "show":
        hide_action = ActionsMenu.addAction(Hide_until_updates_available)
        hide_action.triggered.connect( set_noicon )
        if package_manager_path:
            if show_package_manager and package_manager_enabled:
                ActionsMenu.addSeparator()
                ActionsMenu.addAction(package_manager_name).triggered.connect( start_package_manager0 )
    
    # check we have a package installer
    pl = "mx-packageinstaller packageinstaller"
    from shutil import which
    package_installer = list(filter( lambda x: which(x), pl.split()))[0]
    if package_installer:
        add_Package_Installer_action()

    add_apt_history_action()

    if unattended_upgrade_enabled():
        add_view_unattended_upgrades_logs_action()
        add_view_unattended_upgrades_dpkg_logs_action()

    add_apt_get_update_action()
    add_apt_notifier_help_action()
    if package_manager_path:
        if show_package_manager_help and package_manager_enabled:
            add_package_manager_help_action()

    add_aptnotifier_prefs_action()
    add_about_action()
    add_quit_action()

    cmd = '[ "$XDG_CURRENT_DESKTOP" = "XFCE" ] && '
    cmd+= 'which deartifact-xfce-systray-icons && '
    cmd+= 'deartifact-xfce-systray-icons 1 &'
    subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def add_quit_action():
    ActionsMenu.addSeparator()
    quit_action = ActionsMenu.addAction(QuitIcon,Quit_Apt_Notifier)
    #quit_action.triggered.connect( exit )
    quit_action.triggered.connect( close_notifier )

def close_notifier():
    notification_close()
    sys.exit(0)

def add_apt_notifier_help_action():
    global show_apt_notifier_help
    if show_apt_notifier_help:
        ActionsMenu.addSeparator()
        apt_notifier_help_action = ActionsMenu.addAction(HelpIcon,Apt_Notifier_Help)
        apt_notifier_help_action.triggered.connect(open_apt_notifier_help)

def open_apt_notifier_help():
    systray_icon_hide()
    global conf
    try: conf
    except NameError:
        from aptnotifier_config import AptNotifierConfig
        conf = AptNotifierConfig()
    global show_apt_notifier_help
    show_apt_notifier_help = conf.get("show_apt_notifier_help")
    if not show_apt_notifier_help:
        return
        
    global apt_notifier_help
    try: apt_notifier_help
    except NameError:
        from aptnotifier_help import AptNotifierHelp
        apt_notifier_help = AptNotifierHelp()
        
    apt_notifier_help.apt_notifier_help()
    systray_icon_show()

def add_package_manager_help_action():
    global show_package_manager_help
    global package_manager
    debug_p(f"add_package_manager_help_action : {package_manager}")
    if show_package_manager_help:
        ActionsMenu.addSeparator()
        package_manager_help_action = ActionsMenu.addAction(HelpIcon,Package_Manager_Help)
        package_manager_help_action.triggered.connect(open_package_manager_help)

def open_package_manager_help():
    global show_package_manager_help
    global package_manager
    if not show_package_manager_help:
        return
    if not package_manager:
        return
    systray_icon_hide()

    global apt_notifier_help
    try: apt_notifier_help
    except NameError:
        from aptnotifier_help import AptNotifierHelp
        apt_notifier_help = AptNotifierHelp()
        
    apt_notifier_help.open_package_manager_help(package_manager)

    systray_icon_show()

def add_aptnotifier_prefs_action():
    ActionsMenu.addSeparator()
    aptnotifier_prefs_action =  ActionsMenu.addAction(Apt_Notifier_Preferences)
    aptnotifier_prefs_action.triggered.connect( aptnotifier_prefs )

def add_Package_Installer_action():
    ActionsMenu.addSeparator()
    Package_Installer_action =  ActionsMenu.addAction(Package_Installer)
    Package_Installer_action.triggered.connect( start_package_installer_0 )

def add_apt_history_action():
    ActionsMenu.addSeparator()
    apt_history_action =  ActionsMenu.addAction(Apt_History)
    apt_history_action.triggered.connect( apt_history )

def add_view_unattended_upgrades_logs_action():
    ActionsMenu.addSeparator()
    view_unattended_upgrades_logs_action =  ActionsMenu.addAction(View_Auto_Updates_Logs)
    view_unattended_upgrades_logs_action.triggered.connect( view_unattended_upgrades_logs )

def add_view_unattended_upgrades_dpkg_logs_action():
    ActionsMenu.addSeparator()
    view_unattended_upgrades_logs_action =  ActionsMenu.addAction(View_Auto_Updates_Dpkg_Logs)
    view_unattended_upgrades_logs_action.triggered.connect( view_unattended_upgrades_dpkg_logs )

def add_apt_get_update_action():
    ActionsMenu.addSeparator()
    apt_get_update_action =  ActionsMenu.addAction(Check_for_Updates)
    apt_get_update_action.triggered.connect( apt_get_update )

def add_about_action():
    ActionsMenu.addSeparator()
    about_action =  ActionsMenu.addAction( About )
    about_action.triggered.connect( displayAbout )

def displayAbout():
    notification_close()
    """
    from aptnotifier_about import AptnotifierAbout
    about = AptnotifierAbout()
    about.displayAbout()
    #-------------------
    got those known and not yet fixed error messages:
    qt.qpa.xcb: QXcbConnection: XCB error: 3 (BadWindow), sequence: 1069,
    resource id: 19379270, major code: 40 (TranslateCoords), minor code: 0

    so will run  subprocess with stderr to DEVNULL
    """
    from subprocess import run, DEVNULL
    run(['/usr/bin/python3', '/usr/lib/apt-notifier/modules/aptnotifier_about.py'],
        stderr=DEVNULL, stdout=DEVNULL)

def view_unattended_upgrades_logs():
    notification_close()
    global autoupdate
    try:
        autoupdate
    except NameError:
        from aptnotifier_autoupdate import UnattendedUpgrade
        autoupdate = UnattendedUpgrade()
    autoupdate.view_unattended_upgrades_logs()

def view_unattended_upgrades_dpkg_logs():
    notification_close()
    global autoupdate
    try:
        autoupdate
    except NameError:
        from aptnotifier_autoupdate import UnattendedUpgrade
        autoupdate = UnattendedUpgrade()
    autoupdate.view_unattended_upgrades_dpkg_logs()

def set_QIcons():
    # Define Core objects, Tray icon and QTimer
    global AptIcon
    global QuitIcon
    global icon_config
    global icon_look

    global NoUpdatesIcon
    global NewUpdatesIcon
    global HelpIcon
    global icon_config

    global tray_icon_noupdates
    global tray_icon_newupdates

    NoUpdatesIcon   = QtGui.QIcon(tray_icon_noupdates)
    NewUpdatesIcon  = QtGui.QIcon(tray_icon_newupdates)
    HelpIcon = QtGui.QIcon("/usr/share/icons/oxygen/22x22/apps/help-browser.png")
    QuitIcon = QtGui.QIcon("/usr/share/icons/oxygen/22x22/actions/system-shutdown.png")
    # Create the right-click menu and add the Tooltip text


def systray_icon_hide():
    notification_close()

    cmd = "pgrep -x plasmashell >/dev/null && exit 1 || exit 0"
    running_in_plasma = subprocess.run(cmd, shell=True).returncode
    if not running_in_plasma:
       return

    if not spawn.find_executable("qdbus"):
       return

    Script='''
    var iconName = 'apt-notifier.py';
    for (var i in panels()) {
        p = panels()[i];
        for (var j in p.widgets()) {
            w = p.widgets()[j];
            if (w.type == 'org.kde.plasma.systemtray') {
                s = desktopById(w.readConfig('SystrayContainmentId'));
                s.currentConfigGroup = ['General'];
                var shownItems = s.readConfig('shownItems').split(',');
                if (shownItems.indexOf(iconName) >= 0) {
                    shownItems.splice(shownItems.indexOf(iconName), 1);
                }
                if ( shownItems.length == 0 ) {
                    shownItems = [ 'auto' ];
                }
                s.writeConfig('shownItems', shownItems);
                s.reloadConfig();
            }
        }
    }
    '''
    run = subprocess.Popen(['qdbus org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript "' + Script + '" '],shell=True)

def systray_icon_show():

    cmd = "pgrep -x plasmashell >/dev/null && exit 1 || exit 0"
    running_in_plasma = subprocess.run(cmd, shell=True).returncode
    if not running_in_plasma:
       return

    if not spawn.find_executable("qdbus"):
       return

    Script='''
    var iconName = 'apt-notifier.py';
    for (var i in panels()) {
        p = panels()[i];
        for (var j in p.widgets()) {
            w = p.widgets()[j];
            if (w.type == 'org.kde.plasma.systemtray') {
                s = desktopById(w.readConfig('SystrayContainmentId'));
                s.currentConfigGroup = ['General'];
                var shownItems = s.readConfig('shownItems').split(',');
                if (( shownItems.length == 0 ) || ( shownItems.length == 1 && shownItems[0].length == 0 )) {
                    shownItems = [ iconName ];
                }
                else if (shownItems.indexOf(iconName) === -1) {
                    shownItems.push(iconName)
                }
                if (shownItems.indexOf('auto') >= 0) {
                    shownItems.splice(shownItems.indexOf('auto'), 1);
                }
                s.writeConfig('shownItems', shownItems);
                s.reloadConfig();
            }
        }
    }
    '''
    run = subprocess.Popen(['qdbus org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript "' + Script + '" '],shell=True)

#---------------------------------------------
# notification with actions
#---------------------------------------------
def upgrade_cb(n, action):
    assert action == "upgrade"
    #print("You clicked 'View and Upgrade'")
    #cmd = "apt-notifier-unhide-Icon"
    #run = subprocess.Popen(cmd,shell=True)
    start_viewandupgrade(action)
    n.close()

def reload_cb(n, action):
    assert action == "reload"
    #print("You clicked Reload")
    apt_get_update()
    n.close()

def closed_cb(n):
    #print("Notification closed")
    n.close()

def notification_close():
    global notification
    if notification:
        notification.close()

def desktop_notification(title, msg, icon):
    notify2_initiated = False
    global notification
    notification = False
    try:
        import notify2
    except ImportError:
        return False

    try:
        notify2.init(Updater_Name, 'glib')
        notify2_initiated = True
    except:
        return False

    if  notify2_initiated:
        notification = notify2.Notification(None, icon=icon)
        if ('actions' not in notify2.get_server_caps()):
            return False

        if ('actions' in notify2.get_server_caps()):
            notification.add_action("upgrade", View_and_Upgrade, upgrade_cb)
            notification.add_action("reload", Reload, reload_cb)
        notification.connect('closed', closed_cb)
        notification.timeout = 10000
        notification.update(title, msg)
        notification.show()
        return True
    else:
        return False

def use_notifier():
    global UseNotifier
    global use_dbus_notifications

    if use_dbus_notifications:
        UseNotifier = "dbus"
    else:
        UseNotifier = "qt"
        ret = subprocess.run("pgrep -x xfdesktop".split(), stdout=subprocess.DEVNULL).returncode
        if ret == 0:
            running_in_xfce = True
        else:
            running_in_xfce = False
        if running_in_xfce:
            run = subprocess.run("dpkg-query -f ${Version} -W xfdesktop4".split(), stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, universal_newlines=True)
            xfce_version = run.stdout.strip()
            if xfce_version.startswith("4.16"):
                UseNotifier = "dbus"
            else:
                UseNotifier = "qt"

    debug_p(f"use_notifier(): UseNotifier: {UseNotifier}")
    return UseNotifier

#-----------
def show_popup(popup_title, popup_msg, popup_icon):
    UseNotifier = use_notifier()
    #print( "UseNotifier:" + UseNotifier)

    if not UseNotifier.startswith("qt"):
        if desktop_notification(popup_title, popup_msg, popup_icon):
            return True
        else:
            UseNotifier = "qt"

    if UseNotifier.startswith("qt"):
        def show_message():
            AptIcon.showMessage(popup_title, popup_msg)
        Timer.singleShot(1000, show_message)
        return True

def another_apt_notifer_is_running():
    """
    simple process check for running apt-notifier
    TODO: add a lock 
    """
    from subprocess import run
    import os
    from time import sleep
    euid = str(os.geteuid())
    # python2
    # cmd = [ 'pgrep', '-u' , euid , '-c', '-f',  '/usr/bin/python /usr/bin/apt-notifier.py' ]
    # python3
    # count running apt-notifier processes of current user
    
    cmd = [ 'pgrep', '-u' , euid , '-c', '-f',  '/usr/bin/python3 /usr/lib/apt-notifier/modules/apt-notifier.py' ]
    # check max n times whether another apt-notifer is running
    N=3
    delay = 0.7 
    check = True
    for i in range(N):
        if check:
            res = run(cmd, capture_output=True, text=True)
            ret = res.returncode
            cnt = int(res.stdout.strip())
            debug_p(f"Check aptnotifer is running: {ret} : {cnt}")
            debug_p(f"{cmd}")
            debug_p(f"{' '.join(cmd)}")
            if ret == 0 and cnt > 1:
                # another instance of apt-notifer.py found
                # wait a bit and check again 
                if i+1 < N:
                    sleep(0.7)
                else:
                    break
            else:
                check = False
    
    return check

def run_in_plasma():
    global running_in_plasma
    try: 
        running_in_plasma
    except:
        from subprocess import run
        cmd = "pidof -q plasmashell"
        if run(cmd.split(), capture_output=True).returncode:
            running_in_plasma = False
        else:
            running_in_plasma = True
    #------------------------------
    #if debugging():
    #    running_in_plasma = False
    #    running_in_plasma = True
    #-------------------------------

    return running_in_plasma
  
def debug_p(text=''):
    """ 
    simple debug print helper -  msg get printed to stderr
    """
    if debugging():
        print("Debug: " + text, file = sys.stderr)

def debugging():
    """ 
    simple debugging helper
    """
    import os
    global debug_apt_notifier
    try: 
        debug_apt_notifier
    except:
        try: 
            debug_apt_notifier = os.getenv('DEBUG_APT_NOTIFIER')
        except: 
            debug_apt_notifier = False
    
    return debug_apt_notifier
    
def version_installed():
    from subprocess import run
    cmd = "dpkg-query -f ${Version} -W apt-notifier"
    version_installed = run(cmd.split(), capture_output=True, text=True).stdout.strip()
    return version_installed
    
def restart_apt_notifier():
    from subprocess import run, DEVNULL
    debug_p("restart_apt_notifier.")
    notification_close()
    cmd = "apt-notifier-unhide-Icon & disown -h >/dev/null 2>/dev/null"
    run(cmd, shell=True, executable="/bin/bash")
    sleep(2)

def unattended_upgrade_enabled():
    """
    check whether Unattended-Upgrade is enabled
    """
    from subprocess import run

    cmd = "apt-config shell x APT::Periodic::Unattended-Upgrade/b"
    ret = subprocess.run(cmd.split(), capture_output=True, text=True).stdout
    # ret = "x='true'" : Unattended-Upgrade enabled
    # ret = else       : Unattended-Upgrade not enabled
    if 'true' in ret:
        return True
    else:
        return False
        
            
def get_stat_hash_of_watched_files_and_dirs():
    import os
    import hashlib

    WatchedFiles = """
        /etc/apt/apt.conf
        /etc/apt/preferences
        /var/lib/apt/lists/partial
        /var/cache/apt/pkgcache.bin
        /var/lib/synaptic/preferences
    """

    WatchedDirs = """
        /etc/apt/apt.conf.d
        /etc/apt/preferences.d
        /var/lib/apt
        /var/lib/apt/lists
        /var/lib/dpkg
        /var/cache/apt
    """

    dirs = WatchedDirs.split()
    files = WatchedFiles.split()

    files_in_dirs = [ dir + '/' + x for dir  in dirs for x in os.listdir(dir) ]

    all_files = dirs + files + files_in_dirs

    list_of_files = sorted(all_files)

    tuples_of_times = [ ( os.stat(x).st_mtime, os.stat(x).st_ctime )
                        for x in list_of_files if os.path.exists(x)]


    list_of_times = [ str(time)
                      for tuple in tuples_of_times
                      for time in tuple ]

    msg = '\n'.join(list_of_times)

    md5 = hashlib.md5(msg.encode(encoding='ascii')).hexdigest()

    return md5

def set_debug():
    """ simply set debug environment through commadn line options """
    import os
    debug =  [ '-d', '--debug']
    # using comprehensive
    debug_opts = [x for x in sys.argv if x in debug ]
    # or with lambda filter
    # debug_opts = list(filter(lambda x: x in debug, sys.argv))
    if len(debug_opts) > 0:
        os.environ['DEBUG_APT_NOTIFIER'] = "true"
        print(f"Debug: Debugging {os.getenv('DEBUG_APT_NOTIFIER')}")

def fix_path():
    '''
    set fixed path environment for apt-notifier to run
    '''
    import os
    path = '/usr/local/bin:/usr/bin:/bin:/sbin:/usr/sbin'
    os.environ['PATH'] = path
    
    
#### main #######
def main():
    # Define Core objects, Tray icon and QTimer
    global AptNotify
    global AptIcon
    global QuitIcon
    global icon_config
    global quit_action
    global Timer
    global initialize_aptnotifier_prefs
    global icon_look

    fix_path()
    
    set_debug()

    if another_apt_notifer_is_running():
        debug_p("apt-notifier is already running - exit.")
        sys.exit(1)

    # some early globals
    # check version_at_start
    global version_at_start
    version_at_start = version_installed()
    
    global rc_file_name
    rc_file_name = os.getenv('HOME') + '/.config/apt-notifierrc'
    global message_status
    message_status = "not displayed"
    global notification_icon
    notification_icon = "apt-notifier"


    # fix  fluxbox startup if needed
    fix_fluxbox_startup()
    set_package_manager()
    debug_p(f"set_package_manager() : {package_manager}")

    set_globals()
    initialize_aptnotifier_prefs()
    AptNotify = QtWidgets.QApplication(sys.argv)
    AptIcon = QtWidgets.QSystemTrayIcon()
    Timer = QtCore.QTimer()
    icon_config = read_icon_config()


    # Define the icons:
    global NoUpdatesIcon
    global NewUpdatesIcon
    global HelpIcon

    set_QIcons()

    # Create the right-click menu and add the Tooltip text
    global ActionsMenu
    ActionsMenu = QtWidgets.QMenu()
    AptIcon.activated.connect( left_click_activated )
    Timer.timeout.connect( check_updates )
    # Integrate it together,apply checking of updated packages and set timer to every 1 minute(s) (1 second = 1000)
    AptIcon.setIcon(NoUpdatesIcon)
    check_updates()
    AptIcon.setContextMenu(ActionsMenu)
    if icon_config == "show":
        systray_icon_show()
        AptIcon.show()
    Timer.start(60000)
    if AptNotify.isSessionRestored():
        sys.exit(1)
    sys.exit(AptNotify.exec_())


if __name__ == '__main__':
    main()
