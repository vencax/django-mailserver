'''
Created on Jun 7, 2012

@author: vencax
'''
from django.core.management.base import BaseCommand
import logging

class EmailHandlingCommand(BaseCommand):
    """
    Base for all commands that handles received email.
    """
    def handle(self, *args, **options):
        logging.basicConfig()
        
        recipient = args[0]
        mailfrom = args[1]
        data = ' '.join([unicode(a) for a in args[2:]])
        
        try:
            self.processMail(recipient, mailfrom, data)
        except Exception, e:
            logging.exception(e)
            
    def processMail(self, recipient, mailfrom, data):
        raise NotImplementedError('You must implement processMail method')