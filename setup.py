from setuptools import setup, find_packages

print find_packages()

desc = '''Mailserver that allow whole environment of django\
 apps to interact with incoming mails.'''

setup(
    name='django-mailserver',
    version='0.2',
    description=desc,
    author='Vaclav Klecanda',
    author_email='vencax77@gmail.com',
    url='https://github.com/vencax/django-mailserver',
    packages=find_packages(),
    include_package_data=True,
)