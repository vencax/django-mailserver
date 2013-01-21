'''
Created on Jan 2, 2012

@author: vencax
'''
import os
import smtpd
import asyncore
import logging
import subprocess
import smtplib
import datetime
from settings import Settings


class MailServer(Settings, smtpd.SMTPServer):
    """
    Class based on smtpd server that actually process incoming mails.
    """
    logger = logging.getLogger()

    def __init__(self, **kwargs):
        addr, port, self.logFolder = self.load_config()
        smtpd.SMTPServer.__init__(self, (addr, port), None)

    def process_message(self, peer, mailfrom, rcpttos, data):
        self.logger.info('INCOMING: %s, %s, %s' % (peer, mailfrom, rcpttos))

        try:
            for recipient in rcpttos:
                user, domain = recipient.split('@')
                if domain in self.settings:
                    self._log_mail(domain, data)
                    mapping, forwardaddr, python_binary, script = \
                        self.settings[domain]
                    commandToRun = self._getCommandToRun(user, mapping)
                    if commandToRun:
                        self.runCommand(commandToRun, python_binary, script,
                                        recipient, mailfrom, data)
                        return '250 Ok'
                    else:
                        self.forwardmail(forwardaddr, mailfrom, rcpttos, data)
                        return '250 Ok'
            return '500 Error'  # for not owned mails
        except Exception, e:
            self.logger.error(e)

    def runCommand(self, commandToRun, python_binary, script,
                   recipient, mailfrom, data):
        """
        Process message as django app in given path.
        """
        called = [python_binary, script, commandToRun,
                  recipient, mailfrom, data.replace('\n', ' ')]
        logging.info(' '.join(called))
        self.call(called)

    def call(self, called):
        try:
            retval = subprocess.call(called)
            logging.debug('Retcode: %i' % retval)
        except Exception, e:
            self.logger.exception(e)

    def forwardmail(self, forwardaddr, mailfrom, rcpttos, data):
        self.logger.debug('Forwarding to %s' % forwardaddr)
        try:
            server = smtplib.SMTP('localhost', 25)
            server.sendmail(mailfrom, [forwardaddr], data)
            server.quit()
        except Exception, e:
            self.logger.exception(e)

    def run(self):
        asyncore.loop()

    def stop(self):
        asyncore.close_all()

    # ------------------- privates ---------------------

    def _getCommandToRun(self, user, mapping):
        for regex, command in mapping:
            if regex.match(user):
                return command
        return None

    def _log_mail(self, domain, data):
        if not self.logFolder:
            return
        folder = os.path.join(self.mail_log_folder, domain)
        if not os.path.exists(folder):
            os.mkdir(folder)
        fname = 'mail-%s' % datetime.datetime.now().\
            strftime('%Y-%m-%d_%H-%M-%S')
        with open(os.path.join(folder, fname), 'w') as f:
            f.write(data)


if __name__ == "__main__":
    import signal
    server = MailServer()

    def reload_config(signum, frame):
        server.reload_config()

    signal.signal(signal.SIGUSR1, reload_config)
    server.run()
