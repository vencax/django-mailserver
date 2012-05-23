import os

from fabric.api import *
from fabric.contrib.project import rsync_project
from fabric.contrib import files, console
from fabric import utils
from fabric.decorators import hosts

RSYNC_EXCLUDE = (
    '*.pyc',
    'testsettings',
    'fabfile.py',
)
env.git_repo = 'git://github.com/vencax/django-mailserver.git'
env.project = 'django-mailserver'
env.root = os.path.join('/etc', env.project)
env.configdir = os.path.join(env.root, 'config.d')

def staging():
    """ use staging environment on remote host"""
    utils.abort('Staging deployment not used.')

def production():
    """ use production environment on remote host"""
    env.user = 'vencax'
    env.tmp = os.path.join('/home/', env.user, '.tmp-%s' % env.project)
    env.environment = 'production'
    env.hosts = ['127.0.0.1']
    env.external_interface = 'eth0'

def bootstrap():
    """ initialize remote host environment (virtualenv, deploy, update) """
    run('sudo pip install git+%s' % env.git_repo)
    copy_initscript()
    
def copy_initscript():
    path_to_package = run('''python << EOF
import os
import mailserver
print os.path.dirname(mailserver.__file__)
EOF''')
     
    run('sudo cp %s/initscript.sh /etc/init.d/%s' % (path_to_package, 
                                                     env.project)) 
    run('sudo cp %s/django-mailserver.cfg /etc/' % path_to_package)
    run('sudo chmod 755 /etc/init.d/%s' % env.project)

def enable_init_script():
    """ Enable autostarting of init script """
    run('sudo update-rc defaults django-mailserver')
    
def redirect_port():
    """
    Redirect port 25 on external interface to port 8025
    to allow run the script without root permissions.
    NOTE: currently it is not necessary since starting with root.
    """
    run('sudo iptables -t nat -I PREROUTING --source 0/0 --destination 0/0 -p tcp --dport 25 -j REDIRECT --to-ports 8025 -i %s' % env.external_interface)
    run('sudo iptables -t nat -I OUTPUT --source 0/0 --destination 0/0 -p tcp --dport 25 -j REDIRECT --to-ports 8025 -i %s' % env.external_interface)