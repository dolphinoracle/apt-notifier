#! /usr/bin/python3
# -*- coding: utf-8 -*-
import subprocess
from subprocess import run, PIPE
import sys
import os
from os import environ
import shutil

class AutoStart:
    """
    Check and set apt-notifier autostart
    """
    def __init__(self):

        self.__usr_autostart = environ.get('HOME') + '/.config/autostart/apt-notifier-autostart.desktop'
        self.__xdg_autostart = '/etc/xdg/autostart/apt-notifier-autostart.desktop'
        self.__session = ''
        self.detect_distro()
        self.detect_session()
        
        # patterns to detect  apt-notifier startup
        # used in antiX, future-use in MX
        self.__pat_1 = '[[:space:](]*(sleep [0-9]+[;&[:space:]]+)*(/usr/bin/)?apt-notifier'   
        # current use in MX fluxbox 
        self.__pat_2 = '(nohup sh -c .*)?ionice -c3 nice -n19 nohup( (usr/bin/)?python3?)? /usr/bin/apt-notifier.py'
        # redirects and background &
        self.__dev   = '[)[:space:]]*[12&>dev/null[:space:]]*&[12&>dev/null[:space:]]*'        
        
        self.__pat_1 += self.__dev 
        self.__pat_2 += self.__dev 

        # replace spaces with space-pattern
        self.__pat_2 = self.__pat_2.replace(' ', '[[:space:]]+')

        # leading spaces
        self.__pat_a = '^[[:space:]]*'
        # spaces and hash-signs
        self.__pat_b = '[[:space:]#]*'
        # trailing spaces and comments
        self.__pat_z = '[[:space:]]*(#.*)?$'
        #self.__pat_z = '[[:space:]]*[12&>dev/null[:space:]]*(#.*)?'        

    def detect_distro(self):
        """
        detect distro
        """
        if os.path.exists("/etc/mx-version"):
            self.__distro  = 'MX'
            self.__startup = self.__usr_autostart
        elif os.path.exists("/etc/antix-version"):
            self.__distro = 'antiX'
            self.__startup = environ.get('HOME') + '/.desktop-session/startup'
        else:
            self.__distro = 'other'
            self.__startup = self.__usr_autostart
        
        return self.__distro

    def detect_session(self):
        """
        detect desktop session
        """
        from subprocess import run, PIPE, DEVNULL
        # check fluxbox
        try:
            cmd = 'pidof  fluxbox'
            run(cmd.split(), check=True, stdout=DEVNULL)
            self.__session = 'fluxbox'
            if not self.__distro:
                self.detect_distro()
            if self.__distro != 'antiX':
                self.__startup = environ.get('HOME') + '/.fluxbox/startup'
            return self.__session
        except subprocess.CalledProcessError:
            pass
        # check kde-plasma
        try:
            cmd = 'pidof plasmashell'
            run(cmd.split(), check=True, stdout=DEVNULL)
            self.__session = 'plasma'
            return self.__session
        except subprocess.CalledProcessError:
            pass
        # check XDG_CURRENT_DESKTOP
        if os.getenv('XDG_CURRENT_DESKTOP',''):
            self.__session = os.getenv('XDG_CURRENT_DESKTOP','').lower()
            return self.__session

    def detect_autostart(self):
        """
        detect apt-notifier autostart
        """
        from subprocess import run, PIPE, DEVNULL
        pat_1 = self.__pat_1
        pat_2 = self.__pat_2
        pat_a = self.__pat_a
        pat_z = self.__pat_z

        pattern_1 = pat_a + pat_1 + pat_z
        pattern_2 = pat_a + pat_2 + pat_z

        if not self.__distro:
            self.detect_distro()

        #antiX
        if self.__distro == 'antiX':
            '''
            detect autostart in ~/.desktop-session/startup
            '''
            check1 = run(['grep', '-sqE', pattern_1, self.__startup ])
            if check1.returncode == 0:
                self.__autostart = True
            else:
                self.__autostart = False
        #MX fluxbox
        elif self.__session == 'fluxbox':
            '''
            detect autostart in ~/.fluxbox/startup
            '''
            check1 = run(['grep', '-sqE', pattern_1, self.__startup ])
            check2 = run(['grep', '-sqE', pattern_2, self.__startup ])

            if check1.returncode == 0 or check2.returncode == 0:
                self.__autostart = True
            else:
                self.__autostart = False
        # MX xdg user autostart
        else:
            '''
            detect autostart in xdg autostarts 
            '''
            ret = run(['grep', '-sq', '^Hidden=true', self.__usr_autostart, self.__xdg_autostart ])
            if ret.returncode == 0:
                self.__autostart = False
            else:
                self.__autostart = True
        return self.__autostart

    def disable_autostart(self):
        """
        disable apt-notifier autostart
        """
        from subprocess import run, PIPE, DEVNULL
        autostart = self.detect_autostart()
        if not autostart:
            #print("Autostart already disabled!")
            return autostart
            
        pat_1 = self.__pat_1
        pat_2 = self.__pat_2
        pat_a = self.__pat_a
        pat_b = self.__pat_b
        pat_z = self.__pat_z

        pattern_1 = pat_a + pat_1 + pat_z
        pattern_2 = pat_a + pat_2 + pat_z

        if not self.__distro:
            self.detect_distro()
        #antiX
        if self.__distro == 'antiX':
            '''
            disable autostart in ~/.desktop-session/startup
            '''
            # comment out startup lines found
            run(['sed', '-i', '-r', 's!' + pattern_1 + '!#&!', self.__startup ], stderr=DEVNULL)
            return self.detect_autostart()
        #MX fluxbox
        elif self.__session == 'fluxbox':
            '''
            disable autostart in ~/.fluxbox/startup
            '''
            if run(['grep', '-sqE', pattern_1, self.__startup ]).returncode == 0:
                # comment out startup lines found
                run(['sed', '-i', '-r', 's!' + pattern_1 + '!#&!', self.__startup ], stderr=DEVNULL)
            elif run(['grep', '-sqE', pattern_2, self.__startup ]).returncode == 0:
                # comment out startup lines found
                run(['sed', '-i', '-r', 's!' + pattern_2 + '!#&!', self.__startup ], stderr=DEVNULL)
            return self.detect_autostart()
        #MX or anything else
        else:
            '''
            disable autostart in ~/.config/autostart/apt-notifier-autostart.desktop'
            '''
            try:
              shutil.copyfile(self.__xdg_autostart, self.__usr_autostart)
            except PermissionError:
                print("Error: Permission denied.")
                return False
            except Exception as e:
                print(e)
                print(f"Error occurred while copying file from {self.__xdg_autostart} to {self.__usr_autostart} .")
                print("Error occurred while copying file.")
                return False
            #
            run(['sed', '-i', '-e', '/^Hidden=/d', '-e', '/^Exec=/aHidden=true', self.__usr_autostart ], stderr=DEVNULL)
            return self.detect_autostart()
        return autostart


    def enable_autostart(self):
        """
        enable apt-notifier autostart
        """
        from subprocess import run, PIPE, DEVNULL
        autostart = self.detect_autostart()
        if autostart:
            # print("Autostart already enabled!")
            return autostart

        pat_1 = self.__pat_1
        pat_2 = self.__pat_2
        pat_a = self.__pat_a
        pat_b = self.__pat_b
        pat_z = self.__pat_z

        pattern_1 = pat_a + '#' + pat_b  + '('  + pat_1 + pat_z +')'
        pattern_2 = pat_a + '#' + pat_b  + '('  + pat_2 + pat_z +')'

        if not self.__distro:
            self.detect_distro()

        #antiX
        if self.__distro == 'antiX':
            '''
            enable autostart in ~/.desktop-session/startup
            '''
            # uncomment first startup line found
            run(['sed', '-i', '-r', '0,\!' + pattern_1 + '!s!' + pattern_1 + '!\\1!', self.__startup ], stderr=DEVNULL)
            return self.detect_autostart()

        #MX enable fluxbox startup
        elif self.__session == 'fluxbox':
            '''
            enable autostart in ~/.fluxbox/startup
            '''
            if run(['grep', '-sqE', pattern_1, self.__startup ]).returncode == 0:
                # uncomment first startup line found
                run(['sed', '-i', '-r', '0,\!' + pattern_1 + '!s!' + pattern_2 + '!\\1!', self.__startup ], stderr=DEVNULL)
            elif run(['grep', '-sqE', pattern_2, self.__startup ]).returncode == 0:
                # uncomment first startup line found
                run(['sed', '-i', '-r', '0,\!' + pattern_2 + '!s!' + pattern_2 + '!\\1!', self.__startup ], stderr=DEVNULL)
            return self.detect_autostart()

        #MX non-fluxbox startup
        else:
            '''
            enable autostart in ~/.config/autostart/apt-notifier-autostart.desktop'
            we copy to make it visible in plasma
            '''
            try:
              shutil.copyfile(self.__xdg_autostart, self.__usr_autostart)
            except PermissionError:
                print("Error: Permission denied.")
                return False
            except Exception as e:
                print(e)
                print(f"Error occurred while copying file from {self.__xdg_autostart} to {self.__usr_autostart} .")
                print("Error occurred while copying file.")
                return False
            run(['sed', '-i', '-e', '/^Hidden=/d', self.__usr_autostart ])
            return self.detect_autostart()
        return autostart

    def set_autostart(autostart: bool):

        if autostart:
            if detect_autostart():
                print(f"already set autostart(autostart: {autostart})")
            else:
                print(f"need to enable autostart(autostart: {autostart})")
                enable_autostart()
        else:
            if detect_autostart():
                print(f"need to disable autostart(autostart: False)")
                disable_autostart()
            else:
                print(f"already disabled autostart(autostart: {autostart})")

        return autostart

    @property
    def autostart(self):
        return self.detect_autostart()

    @autostart.setter
    def autostart(self,x):
        if x:
            self.enable_autostart()
        else:
            self.disable_autostart()
        return x


def __run_check_autostart():

    ast = AutoStart()

    print(F"Detected AutoStart: {ast.autostart}")

    """
    print("Toggle AutoStart:")
    if ast.autostart:
        ast.autostart = False
    else:
        ast.autostart = True
    print(ast.autostart)
    """
    
# General application code
def main():

    __run_check_autostart()

if __name__ == '__main__':
    main()

