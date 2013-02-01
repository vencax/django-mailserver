'''
Created on May 22, 2012

@author: vencax
'''
import os
import logging
import re
from projectgroup_settings_iterator.settings import Settings


class MailserverSettings(Settings):
    """
    Loads all setting folder.
    """

    settings_module_name = 'mailserver_settings'

    def process_specific_settings(self, cfgMod):
        self.address = getattr(cfgMod, 'ADDRESS', 'localhost')
        self.port = getattr(cfgMod, 'PORT', 8025)
        logfile = getattr(cfgMod, 'LOGFILE', None)
        self.logFolder = getattr(cfgMod, 'LOG_FOLDER', None)
        level = logging._levelNames[getattr(cfgMod, 'LOGLEVEL', 'WARN')]
        logging.basicConfig(filename=logfile, level=level)

    def process_project_settins(self, proj_sett, proj_path):
        for domainInfo in proj_sett['SETTINGS']:
            domain, mapping, forwardaddr = domainInfo
            mappinginfo = []
            for regex, command in mapping.items():
                mappinginfo.append((re.compile(regex), command))

            python_binary_path = self.path_to_python
            if not self.path_to_python.startswith('/'):
                python_binary_path = os.path.join(proj_path,
                                                  self.path_to_python)

            script = os.path.join(proj_path, self.path_to_manage, 'manage.py')
            self.settings[domain] = (
                mappinginfo, forwardaddr,
                python_binary_path, script
            )
