'''
Created on May 9, 2012

@author: vencax
'''
import smtplib
import unittest
import os
import threading
from mailserver.server import MailServer
from mailserver.settings import Settings

testConfigFile = '/tmp/test-django-mailserver.cfg'
port = 8025
host = 'localhost'
projects_root = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                             'test_project_root')
path_to_project_root = ''
path_to_python = '/usr/bin/python'

def _prepareEnv():    
    os.environ['DJANGO_MAILSERVER_CONF_FILE'] = testConfigFile
    with open(testConfigFile, 'w') as f:
        f.write('%s\n' % projects_root)
        f.write('%s\n' % path_to_project_root)
        f.write('%s\n' % path_to_python)
        f.write('1000\n')
        f.write('%s\n' % host)
        f.write('%i\n' % port)
    
def _runServer():     
    server = MailServer()
    threading.Thread(target=lambda: server.run()).start()    
    return server

def _send_mail(content, addr_from, addr_to):
    
    server=smtplib.SMTP(host, port)    
    msg = ('From: %s\r\nTo: %s\r\n\r\n' % (addr_from, ','.join(addr_to)))
    msg = msg + content
    
    server.sendmail(addr_from, addr_to, msg)
    
    server.quit()
        
class TestSetting(unittest.TestCase):

    def test_settings(self):
        lock = threading.Lock()
        
        projects_root = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                     'test_project_root')
        path_to_project_root = ''
        path_to_python = '/usr/bin/python'
        settings = Settings(projects_root, path_to_project_root, path_to_python,
                            1000, lock)
        settings.load()
        self.assertTrue(len(settings.info) == 2)
        self.assertTrue('example1.com' in settings.info)
        self.assertTrue(settings.info['example1.com'][1] == 'domainwide_forward@address.com')
        
class TestReceiveMail(unittest.TestCase):
        
    def test_send(self):
        _prepareEnv()
        self.server = _runServer()
        
        addr_from = 'vencax@noexists.com'
        addr_to = ['vencax77@example1.com']
    
        _send_mail('ahoj franto', addr_from, addr_to)


if __name__ == '__main__':
    unittest.main()