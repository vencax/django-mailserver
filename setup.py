import subprocess
from setuptools import setup, find_packages
from setuptools.command.install import install
import os

desc = '''Mailserver that allow whole environment of django\
 apps to interact with incoming mails.'''
installScript = '/etc/init.d/django-mailserver'
 
class MyInstall(install):
    def run(self):
        if os.path.exists(installScript):
            subprocess.call([installScript, 'stop'])
        install.run(self)
        subprocess.call(['chmod', 'a+x', installScript])
        subprocess.call([installScript, 'start'])

setup(
    name='django-mailserver',
    version='0.3',
    description=desc,
    author='Vaclav Klecanda',
    author_email='vencax77@gmail.com',
    url='https://github.com/vencax/django-mailserver',
    data_files=[
        ('/etc/init.d/', ['django-mailserver']),
    ],
    packages=find_packages(),
    dependency_links=[
        'https://github.com/vencax/django-projectgroup-settings-iterator'
    ],
    include_package_data=True,
    cmdclass={'install': MyInstall},
)
