'''
Created on Jan 2, 2012

@author: vencax
'''
import smtpd
import asyncore
import logging
import threading
import subprocess
import smtplib

from settings import Settings
import os


class MailServer(smtpd.SMTPServer):
    """
    Class based on smtpd server that actually process incoming mails.
    """
    logger = logging.getLogger()

    def __init__(self, **kwargs):
        projects_root, path_to_project_root, path_to_python,\
            poll_interval, addr, port = self._load_config()
            
        smtpd.SMTPServer.__init__(self, (addr, port), None)
        
        self._settingslock = threading.Lock()    
        self._settings = Settings(projects_root,
                                  path_to_project_root,
                                  path_to_python,
                                  poll_interval,
                                  self._settingslock)
        self._settings.load()

    def process_message(self, peer, mailfrom, rcpttos, data):
        self.logger.info('INCOMING: %s, %s, %s' % (peer, mailfrom, rcpttos))

        self._settingslock.acquire()
        for recipient in rcpttos:
            user, domain = recipient.split('@')
            if domain in self._settings.info:
                mapping, forwardaddr, python_binary, script = self._settings.info[domain]
                commandToRun = self._getCommandToRun(user, mapping)
                if commandToRun:
                    self._processAsDjango(python_binary, script, commandToRun, 
                                          recipient, mailfrom, data)
                else:
                    self._forward(forwardaddr, mailfrom, rcpttos, data)
            self._settingslock.release()

    def run(self):
        self._settings.run()
        asyncore.loop()

    # ------------------- privates ---------------------
    
    def _getCommandToRun(self, user, mapping):
        for regex, command in mapping:
            if regex.match(user):
                return command
        return None

    def _forward(self, address, mailfrom, rcpttos, message):
        try:
            server=smtplib.SMTP('localhost', 25)
            server.sendmail(mailfrom, [address], message)
            server.quit()
        except Exception, e:
            self.logger.exception(e)

    def _processAsDjango(self, python_binary, script, commandToRun, 
                         recipient, mailfrom, data):
        """
        Process message as django app in given path.
        """
        try:
            subprocess.call([python_binary, script, commandToRun, 
                             recipient, mailfrom, data])
        except Exception, e:
            self.logger.exception(e)

    def _load_config(self):
        if 'DJANGO_MAILSERVER_CONF_FILE' in os.environ:
            configfile = os.environ['DJANGO_MAILSERVER_CONF_FILE']
        else:
            configfile = '/etc/django-mailserver.cfg'
            
        with open(configfile, 'r') as f:
            projects_root = f.readline().strip('\n')
            if not os.path.exists(projects_root):
                raise Exception('projects_root folder %s not exists.' % projects_root)
            path_to_project_root = f.readline().strip('\n')
            path_to_python = f.readline().strip('\n')
            poll_interval = int(f.readline().strip('\n'))
            address = f.readline().strip('\n')
            port = int(f.readline().strip('\n'))
            logfile = f.readline().strip('\n')
            level = logging._levelNames.get(f.readline().strip('\n'), 'WARN')            
            logging.basicConfig(filename=logfile, level=level)
            return projects_root, path_to_project_root, path_to_python, \
                poll_interval, address, port

if __name__ == "__main__":    
    server = MailServer()
    server.run()