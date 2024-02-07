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

##############################################################################
#                         Configuration Section                              #
##############################################################################

default_domain_name=admin.mydomain.com

# Loading Default Data
#  if set to "yes", default data sets will be loaded without prompting.
skip_prompts="no"

# Scaling and Clustering Options
core_sequence_increment=10
core_sequence_start=1001

########################### Configuration End ################################
##############################################################################

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
    echo -e "${c_red}You must be logged in as root or su - root to run this reset to defaults.${c_clear}"
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
pbx_prompt n "Reset DjangoPBX - Are you sure (y/n)? "
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    exit 1
fi
echo -e $c_red
cat << EOF
**************************************************************
* This script will destroy your current Django-PBX database! *
**************************************************************

Actions that will be performed:
1. Drop schema pubic
2. Create new public schema
3. Run migrations
4. Create new DjangoPBX superuser
5. Load default data

You will be prompted for some of the data loads.

EOF
echo -en $c_clear 
pbx_prompt n "Are you really sure that you wish to continue (y/n)? "
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    exit 1
fi

if [ ! -f /home/django-pbx/pbx/pbx/settings.py ]; then
    echo -e "${c_red}A valid DjangoPBX installation does not exist.${c_clear}"
    exit 1
fi

t_now=`/bin/date +"%Y%m%d%H%M"`
db_backup=/tmp/djangopbx_db_${t_now}.sql
cwd=$(pwd)
cd /tmp

echo -e "${c_green}Making a backup of your databse to ${db_backup}${c_clear}"
sudo -u postgres pg_dump --verbose -Fc djangopbx --schema=public -f ${db_backup}
echo -e $c_cyan
echo " "
echo "Database backup complete"
echo " "
echo "You can restore your data, if required,  with the following commands:"
echo "su - postgres"
echo "pg_restore -v -Fc --dbname=djangopbx ${db_backup}"
echo "exit"
echo -en $c_clear 
sudo -u postgres psql -d djangopbx -c "drop schema public cascade;"
sudo -u postgres psql -d djangopbx -c "create schema public;"
echo " "
echo "Performing migrations..."
sudo -u django-pbx bash -c 'source ~/envdpbx/bin/activate && cd /home/django-pbx/pbx && python3 manage.py migrate'
echo " "
echo "Loading user groups..."
sudo -u django-pbx bash -c 'source ~/envdpbx/bin/activate && cd /home/django-pbx/pbx && python3 manage.py loaddata --app tenants group.json'
echo " "
echo "Setting Django Core Sequences..."
sudo -u postgres psql -d djangopbx -c "alter sequence if exists auth_group_id_seq increment by ${core_sequence_increment} restart with ${core_sequence_start};"
sudo -u postgres psql -d djangopbx -c "alter sequence if exists auth_permission_id_seq increment by ${core_sequence_increment} restart with ${core_sequence_start};"
sudo -u postgres psql -d djangopbx -c "alter sequence if exists auth_user_id_seq increment by ${core_sequence_increment} restart with ${core_sequence_start};"
sudo -u postgres psql -d djangopbx -c "alter sequence if exists django_admin_log_id_seq increment by ${core_sequence_increment} restart with ${core_sequence_start};"
sudo -u postgres psql -d djangopbx -c "alter sequence if exists django_content_type_id_seq increment by ${core_sequence_increment} restart with ${core_sequence_start};"
sudo -u postgres psql -d djangopbx -c "alter sequence if exists pbx_users_id_seq increment by ${core_sequence_increment} restart with ${core_sequence_start};"

sleep 1
echo -e $c_green
echo "You are about to create a superuser to manage DjangoPBX, please use a strong, secure password."
echo -e "Hint: Use the email format for the username e.g. <user@${default_domain_name}>"
pbx_prompt n "Press any key to continue "
sudo -u django-pbx bash -c 'source ~/envdpbx/bin/activate && cd /home/django-pbx/pbx && python3 manage.py createsuperuser'

###############################################
# Basic Data loading
###############################################
sudo -u django-pbx bash -c "source ~/envdpbx/bin/activate && cd /home/django-pbx/pbx && python3 manage.py createpbxdomain --domain ${default_domain_name} --user ${core_sequence_start}"

pbx_prompt $skip_prompts "Load Default Access controls? "
if [[ $REPLY =~ ^[Yy]$ ]]
then
    sudo -u django-pbx bash -c 'source ~/envdpbx/bin/activate && cd /home/django-pbx/pbx && python3 manage.py loaddata --app switch accesscontrol.json'
    sudo -u django-pbx bash -c 'source ~/envdpbx/bin/activate && cd /home/django-pbx/pbx && python3 manage.py loaddata --app switch accesscontrolnode.json'
fi

pbx_prompt $skip_prompts "Load Default Email Templates? "
if [[ $REPLY =~ ^[Yy]$ ]]
then
    sudo -u django-pbx bash -c 'source ~/envdpbx/bin/activate && cd /home/django-pbx/pbx && python3 manage.py loaddata --app switch emailtemplate.json'
fi

pbx_prompt $skip_prompts "Load Default Modules data? "
if [[ $REPLY =~ ^[Yy]$ ]]
then
    sudo -u django-pbx bash -c 'source ~/envdpbx/bin/activate && cd /home/django-pbx/pbx && python3 manage.py loaddata --app switch modules.json'
fi

pbx_prompt $skip_prompts "Load Default SIP profiles? "
if [[ $REPLY =~ ^[Yy]$ ]]
then
    sudo -u django-pbx bash -c 'source ~/envdpbx/bin/activate && cd /home/django-pbx/pbx && python3 manage.py loaddata --app switch sipprofile.json'
    sudo -u django-pbx bash -c 'source ~/envdpbx/bin/activate && cd /home/django-pbx/pbx && python3 manage.py loaddata --app switch sipprofiledomain.json'
    sudo -u django-pbx bash -c 'source ~/envdpbx/bin/activate && cd /home/django-pbx/pbx && python3 manage.py loaddata --app switch sipprofilesetting.json'
fi

pbx_prompt $skip_prompts "Load Default Switch Variables? "
if [[ $REPLY =~ ^[Yy]$ ]]
then
    sudo -u django-pbx bash -c 'source ~/envdpbx/bin/activate && cd /home/django-pbx/pbx && python3 manage.py loaddata --app switch switchvariable.json'
fi

pbx_prompt $skip_prompts "Load Default Music on Hold data? "
if [[ $REPLY =~ ^[Yy]$ ]]
then
    sudo -u django-pbx bash -c 'source ~/envdpbx/bin/activate && cd /home/django-pbx/pbx && python3 manage.py loaddata --app musiconhold musiconhold.json'
    sudo -u django-pbx bash -c 'source ~/envdpbx/bin/activate && cd /home/django-pbx/pbx && python3 manage.py loaddata --app musiconhold mohfile.json'
fi

pbx_prompt $skip_prompts "Load Number Translation data? "
if [[ $REPLY =~ ^[Yy]$ ]]
then
    sudo -u django-pbx bash -c 'source ~/envdpbx/bin/activate && cd /home/django-pbx/pbx && python3 manage.py loaddata --app numbertranslations numbertranslations.json'
    sudo -u django-pbx bash -c 'source ~/envdpbx/bin/activate && cd /home/django-pbx/pbx && python3 manage.py loaddata --app numbertranslations numbertranslationdetails.json'
fi

pbx_prompt $skip_prompts "Load Conference Settings? "
if [[ $REPLY =~ ^[Yy]$ ]]
then
    sudo -u django-pbx bash -c 'source ~/envdpbx/bin/activate && cd /home/django-pbx/pbx && python3 manage.py loaddata --app conferencesettings conferencecontrols.json'
    sudo -u django-pbx bash -c 'source ~/envdpbx/bin/activate && cd /home/django-pbx/pbx && python3 manage.py loaddata --app conferencesettings conferencecontroldetails.json'
    sudo -u django-pbx bash -c 'source ~/envdpbx/bin/activate && cd /home/django-pbx/pbx && python3 manage.py loaddata --app conferencesettings conferenceprofiles.json'
    sudo -u django-pbx bash -c 'source ~/envdpbx/bin/activate && cd /home/django-pbx/pbx && python3 manage.py loaddata --app conferencesettings conferenceprofileparams.json'
fi

###############################################
# Default Settings
###############################################
pbx_prompt $skip_prompts "Load Default Settings? "
if [[ $REPLY =~ ^[Yy]$ ]]
then
    sudo -u django-pbx bash -c 'source ~/envdpbx/bin/activate && cd /home/django-pbx/pbx && python3 manage.py loaddata --app tenants defaultsetting.json'
    sudo -u django-pbx bash -c "source ~/envdpbx/bin/activate && cd /home/django-pbx/pbx && python3 manage.py updatedefaultsetting --category cluster --subcategory switch_name_1 --value $HOSTNAME"
    sudo -u django-pbx bash -c "source ~/envdpbx/bin/activate && cd /home/django-pbx/pbx && python3 manage.py updatedefaultsetting --category cluster --subcategory message_broker_password --value $rabbitmq_password"
fi

pbx_prompt $skip_prompts "Load Default Provision Settings? "
if [[ $REPLY =~ ^[Yy]$ ]]
then
    sudo -u django-pbx bash -c 'source ~/envdpbx/bin/activate && cd /home/django-pbx/pbx && python3 manage.py loaddata --app provision commonprovisionsettings.json'
fi

pbx_prompt $skip_prompts "Load Yealink Provision Settings? "
if [[ $REPLY =~ ^[Yy]$ ]]
then
    sudo -u django-pbx bash -c 'source ~/envdpbx/bin/activate && cd /home/django-pbx/pbx && python3 manage.py loaddata --app provision yealinkprovisionsettings.json'
fi

pbx_prompt $skip_prompts "Load Yealink vendor provision data? "
if [[ $REPLY =~ ^[Yy]$ ]]
then
    sudo -u django-pbx bash -c 'source ~/envdpbx/bin/activate && cd /home/django-pbx/pbx && python3 manage.py loaddata --app provision devicevendors.json'
    sudo -u django-pbx bash -c 'source ~/envdpbx/bin/activate && cd /home/django-pbx/pbx && python3 manage.py loaddata --app provision devicevendorfunctions.json'
fi

###############################################
# Menu Defaults
###############################################
pbx_prompt n "Load Menu Defaults? "
if [[ $REPLY =~ ^[Yy]$ ]]
then
    sudo -u django-pbx bash -c 'source ~/envdpbx/bin/activate && cd /home/django-pbx/pbx && python3 manage.py menudefaults'
fi


cd $cwd
echo " "
echo -e "${c_green}Reset Complete"
echo -e "${c_yellow}Thankyou for using DjangoPBX"
echo -e $c_clear
