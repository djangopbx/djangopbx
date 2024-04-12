#!/bin/bash
#
#    DjangoPBX
#
#    MIT License
#
#    Copyright (c) 2016 - 2024 Adrian Fretwell <adrian@djangopbx.com>
#
#    Permission is hereby granted, free of charge, to any person obtaining a copy
#    of this software and associated documentation files (the "Software"), to deal
#    in the Software without restriction, including without limitation the rights
#    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#    copies of the Software, and to permit persons to whom the Software is
#    furnished to do so, subject to the following conditions:
#
#    The above copyright notice and this permission notice shall be included in all
#    copies or substantial portions of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#    SOFTWARE.
#
#    Contributor(s):
#    Adrian Fretwell <adrian@djangopbx.com>
#

#################### Define Generic Update Functions #########################
pbx_prompt() {
    if [[ $1 == "yes" ]]
    then
        REPLY=Y
    else
        echo -e $c_yellow
        read -p "$2" -n 1 -r
        echo -e $c_clear
    fi
}

######################## Define Color variables ##############################
c_red='\033[1;31m'
c_green='\033[1;32m'
c_yellow='\033[1;33m'
c_blue='\033[1;34m'
c_cyan='\033[1;36m'
c_white='\033[1;37m'
c_clear='\033[0m'

######################## Start of Generic Update #############################
echo -e $c_cyan
cat << 'EOF'

 ____  _                         ____  ______  __
|  _ \(_) __ _ _ __   __ _  ___ |  _ \| __ ) \/ /
| | | | |/ _` | '_ \ / _` |/ _ \| |_) |  _ \\  /
| |_| | | (_| | | | | (_| | (_) |  __/| |_) /  \
|____// |\__,_|_| |_|\__, |\___/|_|   |____/_/\_\
    |__/             |___/

EOF
if [ "`id -u`" -gt 0 ]; then
    echo -e "${c_red}You must be logged in as root or su - root to run this generic update.${c_clear}"
    exit 1
fi
term_user=$(logname)

if [[ $term_user != "root" ]]
then
echo -e $c_green
cat << EOF
If you have used su to aquire root privileges, please make sure you
have also aquired the correct PATH environment for root.
It is strongly recommended that you use su - root rather than plain su.

If you are unsure, quit generic update and check your PATH variable, we
would expect to see at least one reference to /sbin or /usr/sbin in your PATH.
Your PATH is shown below:

EOF
echo -en $c_white 
echo $PATH
echo
fi
pbx_prompt n "Update DjangoPBX - Are you sure (y/n)? "
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    exit 1
fi

if [ ! -f /home/django-pbx/pbx/pbx/settings.py ]; then
    echo -e "${c_red}A valid DjangoPBX installation does not exist.${c_clear}"
    exit 1
fi

t_now=`/bin/date +"%Y%m%d%H%M"`

echo -e "${c_green}Making a backup of your settings.py file.${c_clear}"
mkdir -p /home/django-pbx/pbx-backups/settings
chown django-pbx:django-pbx /home/django-pbx/pbx-backups
chown django-pbx:django-pbx /home/django-pbx/pbx-backups/settings
cp /home/django-pbx/pbx/pbx/settings.py /home/django-pbx/pbx-backups/settings/settings.${t_now}.py
echo -e "${c_blue}Settings saved to /home/django-pbx/pbx-backups/settings/settings.${t_now}.py${c_clear}"

cwd=$(pwd)
cd /tmp

echo " "
echo "Checking git synchronisation..."
sudo -u django-pbx bash -c 'cd /home/django-pbx/pbx && git pull'
if [ $? -gt 0 ]; then
    echo -e "${c_red}The git pull resulted in an error.${c_clear}"
    echo -e "${c_green}It is often OK to proceed with a git stash then pull."
    echo -e "Git may promot you for a commit reason.  if so"
    echo -e "just accept the defaults and if presented with an editor, use Ctrl-X"
    echo -e "to exit and save any changes.${c_clear}"
    pbx_prompt n "Proceed with Stash and Pull (y/n)? "
    if [[ $REPLY =~ ^[Yy]$ ]]
    then
        sudo -u django-pbx bash -c 'cd /home/django-pbx/pbx && git stash'
        sudo -u django-pbx bash -c 'cd /home/django-pbx/pbx && git pull'
        sudo -u django-pbx bash -c 'cd /home/django-pbx/pbx && git stash pop'
    else
        pbx_prompt n "Would you like to abort the upgrade (y/n)? "
        if [[ $REPLY =~ ^[Yy]$ ]]
        then
        echo " "
        echo -e "${c_green}Generic Update Terminated"
        echo -e $c_clear
        exit 1
        fi
    fi
    echo -e "The following is an output from git status."
    echo -e "If you have any modified or extra files this will tell you what they are:"
    sudo -u django-pbx bash -c 'cd /home/django-pbx/pbx && git status'
    pbx_prompt n "Press any key to contine... "
fi

###############################################
# Python Dependencies
###############################################
pbx_prompt n "Update dependencies requirements.txt (recommended)? "
if [[ $REPLY =~ ^[Yy]$ ]]
then
    sudo -u django-pbx bash -c 'source ~/envdpbx/bin/activate && pip3 install -r /home/django-pbx/pbx/requirements.txt'
fi

###############################################
# Database and Static Files
###############################################
echo " "
echo "Performing migrations..."
sudo -u django-pbx bash -c 'source ~/envdpbx/bin/activate && cd /home/django-pbx/pbx && python3 manage.py migrate'
echo " "
echo "Collecting Static Webserver files, safe to say yes to this..."
sudo -u django-pbx bash -c 'source ~/envdpbx/bin/activate && cd /home/django-pbx/pbx && python3 manage.py collectstatic'

###############################################
# Menu Defaults
###############################################
pbx_prompt n "Load Menu Defaults? "
if [[ $REPLY =~ ^[Yy]$ ]]
then
    rm -f /home/django-pbx/pbx/portal/fixtures/defaultmenudata.loaded
    rm -f /home/django-pbx/pbx/portal/fixtures/defaultmenuitemgroup.loaded
    sudo -u django-pbx bash -c 'source ~/envdpbx/bin/activate && cd /home/django-pbx/pbx && python3 manage.py menudefaults'
fi

###############################################
# Dialplan Defaults
###############################################
pbx_prompt n "Load Dialplan Defaults? "
if [[ $REPLY =~ ^[Yy]$ ]]
then
    sudo -u django-pbx bash -c 'source ~/envdpbx/bin/activate && cd /home/django-pbx/pbx && python3 manage.py dialplandefaults'
fi
cd $cwd

###############################################
# Update freeswitch files
###############################################
echo " "
echo "Updating freeswitch files..."
rsync --ignore-existing -avz /home/django-pbx/pbx/switch/resources/templates/conf/autoload_configs/ /home/django-pbx/freeswitch/autoload_configs

###############################################
# Update system files
###############################################
echo " "
echo "Updating system files..."
rsync --update -avz /home/django-pbx/pbx/pbx/resources/usr/ /

###############################################
# Update system files from installed
# applications
###############################################
echo " "
echo "Updating application specific system files..."
for DIRECTORY in /home/django-pbx/pbx/*/resources/system_files/; do
    if [ -d "$DIRECTORY" ]; then
        rsync --update -avz $DIRECTORY /
    fi
done

###############################################
# Reload uWSGI
###############################################
uwsgi --reload /var/run/uwsgi/app/fs_config/pid
uwsgi --reload /var/run/uwsgi/app/djangopbx/pid

###############################################
# Checking for modified files
###############################################
echo " "
echo "Checking for modified files..."
diff /home/django-pbx/pbx/pbx/resources/etc/sudoers.d/django_pbx_sudo_inc /etc/sudoers.d/django_pbx_sudo_inc > /tmp/pbx-generic-update.tmp
if [ $? -gt 0 ]; then
echo -e "${c_cyan}Your /etc/sudoers.d/django_pbx_sudo_inc differs from the distribution file..."
echo -e $c_white
cat /tmp/pbx-generic-update.tmp
echo -e $c_clear
fi
diff /home/django-pbx/pbx/pbx/resources/home/django-pbx/crontab /home/django-pbx/crontab > /tmp/pbx-generic-update.tmp
if [ $? -gt 0 ]; then
echo -e "${c_cyan}Your /home/django-pbx/crontab differs from the distribution file..."
echo -e $c_white
cat /tmp/pbx-generic-update.tmp
echo -e $c_clear
fi


echo " "
echo -e "${c_green}Generic Update Complete"
echo -e "${c_yellow}Thankyou for using DjangoPBX"
echo -e $c_clear
