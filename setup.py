from setuptools import setup, find_packages

print find_packages()

desc = '''Mailserver that allow whole environment of django\
 apps to interact with incoming mails.'''

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
    install_requires=[
        'git+git://github.com/vencax/django-projectgroup-settings-iterator.git'
    ],
    include_package_data=True,
)
