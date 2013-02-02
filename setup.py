import subprocess
from setuptools import setup, find_packages
from setuptools.command.install import install

desc = '''Mailserver that allow whole environment of django\
 apps to interact with incoming mails.'''
 
class MyInstall(install):
    def run(self):
        subprocess.call(['/etc/init.d/django-mailserver', 'stop'])
        install.run(self)
        subprocess.call(['chmod', 'a+x', '/etc/init.d/django-mailserver'])
        subprocess.call(['/etc/init.d/django-mailserver', 'start'])

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
