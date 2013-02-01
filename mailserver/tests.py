'''
Created on May 9, 2012

@author: vencax
'''
import smtplib
import unittest
import threading
import time
from projectgroup_settings_iterator.tests import DjangoProjectRootTestCase
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


class TestSetting(DjangoProjectRootTestCase):

    testDomains = ('example1.com', 'example2.com', 'sample2.net')
    settings_module_name = 'mailserver_settings'

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

    def prepareConfigExtras(self, cfgfilestram):
        self.host = 'localhost'
        self.port = 8025
        cfgfilestram.write('PORT=%s\n' % self.port)
        cfgfilestram.write('LOGLEVEL=\'DEBUG\'\n')

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
