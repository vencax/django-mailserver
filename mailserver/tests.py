'''
Created on May 9, 2012

@author: vencax
'''
import smtplib
import unittest
import os
import threading
import shutil
import time
from mailserver.server import MailServer


class TestingMailServer(MailServer):
    def __init__(self):
        super(TestingMailServer, self).__init__()
        self.forward = []
        self.runqueue = []

    def call(self, called):
        self.runqueue.append(called)

    def forwardmail(self, forwardaddr, mailfrom, rcpttos, data):
        self.forward.append((forwardaddr, mailfrom, rcpttos, data))


class TestSetting(unittest.TestCase):

    testDomains = ('example1.com', 'example2.com', 'sample2.net')

    def setUp(self):
        unittest.TestCase.setUp(self)
        self._prepareEnv()

    def test_all(self):
        self.server = TestingMailServer()

        for desired, actual in \
            zip(sorted(self.testDomains), sorted(self.server.settings)):
            self.assertTrue(actual == desired)
            self.assertTrue(self.server.settings[desired][1] == \
                            'domainwide_forward@address.com')

        self._runServer()

        addr_from = 'vencax@noexists.com'

        try:
            self._send_mail('ahoj franto', addr_from,
                        ['user@unlistedDomain.com'])
            raise AssertionError('SMTPDataError expected')
        except smtplib.SMTPDataError:
            pass

        self._send_mail('ahoj franto', addr_from,
                        ['vencax77@%s' % self.testDomains[0]])
        self._send_mail('ahoj franto', addr_from,
                        ['accountcallback@%s' % self.testDomains[1]])
        time.sleep(1)

        desiredForwarded = [
            ('domainwide_forward@address.com',
             'vencax@noexists.com',
             ['vencax77@%s' % self.testDomains[0]],
             'From: %s\nTo: vencax77@%s\n\nahoj franto' % \
                (addr_from, self.testDomains[0]))
        ]
        desiredCalled = [
            [self.server.settings[self.testDomains[1]][2],
             self.server.settings[self.testDomains[1]][3],
             'onAccountCallback',
             'accountcallback@example2.com',
             'vencax@noexists.com',
             'From: %s To: accountcallback@%s  ahoj franto' % \
                (addr_from, self.testDomains[1])]
        ]
        assert self.server.forward == desiredForwarded, \
        'expected:\n%s\nactual:\n%s' % (desiredForwarded, self.server.forward)
        assert self.server.runqueue == desiredCalled, \
        'expected:\n%s\nactual:\n%s' % (desiredCalled, self.server.runqueue)

    def tearDown(self):
        self.server.stop()
        shutil.rmtree(self._test_root)
        unittest.TestCase.tearDown(self)

    def _prepareEnv(self):
        _proj_root = os.path.dirname(os.path.dirname(__file__))
        _test_root = os.path.join(_proj_root, '_testTMP')
        self._test_root = _test_root
        if os.path.exists(_test_root):
            shutil.rmtree(_test_root)
        os.mkdir(_test_root)

        testConfigFile = os.path.join(_test_root, '_example_cfg.py')
        os.environ['DJANGO_MAILSERVER_CONF_FILE'] = testConfigFile

        self.port = 8025
        self.host = 'localhost'
        projects_root = os.path.join(_test_root, 'test_project_root')
        os.mkdir(projects_root)

        path_to_project_root = 'mysite'
        path_to_python = 'virtenv/bin/python'
        with open(testConfigFile, 'w') as f:
            f.write('PROJECTS_ROOT=\'%s\'\n' % projects_root)
            f.write('PATH_TO_PROJECT_ROOT=\'%s\'\n' % path_to_project_root)
            f.write('PATH_TO_PYTHON=\'%s\'\n' % path_to_python)
            f.write('PATH_TO_MANAGE=\'\'\n')
            f.write('PORT=%s\n' % self.port)
            f.write('LOGLEVEL=\'DEBUG\'\n')

        for p in self.testDomains:
            self._create_domain_fldr(p, projects_root, path_to_project_root)

    def _create_domain_fldr(self, domain, projects_root, path_to_project_root):
        domFolder = os.path.join(projects_root, domain)
        os.mkdir(domFolder)
        projRoot = os.path.join(domFolder, path_to_project_root)
        os.mkdir(projRoot)
        f = open(os.path.join(projRoot, '__init__.py'), 'w')
        f.close()
        with open(os.path.join(projRoot, 'mailserver_settings.py'), 'w') as f:
            cntnt = '''
settings = [
    ('%s', {
        'accountcallback': 'onAccountCallback',
        'whateverElse': 'onWhaeverElse'
    }, 'domainwide_forward@address.com')
]'''
            f.write(cntnt % domain)

    def _runServer(self):
        threading.Thread(target=lambda: self.server.run()).start()

    def _send_mail(self, content, addr_from, addr_to):
        server = smtplib.SMTP(self.host, self.port)
        msg = ('From: %s\r\nTo: %s\r\n\r\n' % \
               (addr_from, ','.join(addr_to)))
        msg = msg + content

        server.sendmail(addr_from, addr_to, msg)
        server.quit()


if __name__ == '__main__':
    unittest.main()
