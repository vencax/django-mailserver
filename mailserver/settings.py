'''
Created on May 22, 2012

@author: vencax
'''
import os
import logging
import re
import sys


class Settings(object):
    """
    Loads all setting folder.
    """

    def load_config(self):
        if 'DJANGO_MAILSERVER_CONF_FILE' in os.environ:
            configfile = os.environ['DJANGO_MAILSERVER_CONF_FILE']
        else:
            configfile = '/etc/django_mailserver_cfg.py'

        cfgPath = os.path.dirname(configfile)
        cfgModName = os.path.basename(configfile).rstrip('.py')
        sys.path.insert(0, cfgPath)

        cfgMod = __import__(cfgModName)

        projects_root = getattr(cfgMod, 'PROJECTS_ROOT', '/home')
        if not os.path.exists(projects_root):
            raise Exception('PROJECTS_ROOT %s not exists.' % projects_root)

        path_to_project_root = getattr(cfgMod, 'PATH_TO_PROJECT_ROOT',
                                       'mysite')
        path_to_python = getattr(cfgMod, 'PATH_TO_PYTHON', 'virtenv/bin')
        path_to_manage = getattr(cfgMod, 'PATH_TO_MANAGE', 'mysite')
        address = getattr(cfgMod, 'ADDRESS', 'localhost')
        port = getattr(cfgMod, 'PORT', 8025)
        logfile = getattr(cfgMod, 'LOGFILE', None)
        logFolder = getattr(cfgMod, 'LOG_FOLDER', None)
        level = logging._levelNames[getattr(cfgMod, 'LOGLEVEL', 'WARN')]
        logging.basicConfig(filename=logfile, level=level)

        self._load_configs(projects_root, path_to_project_root,
                           path_to_python, path_to_manage)

        self.projects_root = projects_root
        self.path_to_project_root = path_to_project_root
        self.path_to_python = path_to_python
        self.path_to_manage = path_to_manage
        return address, port, logFolder

    def reload_config(self):
        self._load_configs(self.projects_root, self.path_to_project_root,
                           self.path_to_python, self.path_to_manage)

    # -------------------------- privates -------------------------------------

    def _load_configs(self, projects_root, path_to_project_root,
                      path_to_python, path_to_manage):
        self.settings = {}
        for project in os.listdir(projects_root):
            projPath = os.path.join(projects_root, project)
            if not os.path.isdir(projPath) or project.startswith('.'):
                continue

            project_root = os.path.join(projPath, path_to_project_root)
            proj_sett = self._load_project_settings(project, project_root)
            if proj_sett:
                logging.debug('Found settings in %s' % project_root)
                proj_path_to_manage = \
                    os.path.join(projects_root, project, path_to_manage)
                self._add_project_settings(proj_sett, project, path_to_python,
                                           proj_path_to_manage, projects_root)
        logging.debug('Settings loaded')

    def _add_project_settings(self, proj_settings, project, path_to_python,
                              path_to_manage, projects_root):
        for domainInfo in proj_settings:
            domain, mapping, forwardaddr = domainInfo
            mappinginfo = []
            for regex, command in mapping.items():
                mappinginfo.append((re.compile(regex), command))

            python_binary_path = path_to_python
            if not path_to_python.startswith('/'):
                python_binary_path = os.path.join(projects_root,
                            project, path_to_python)

            script = os.path.join(path_to_manage, 'manage.py')
            self.settings[domain] = (
                mappinginfo, forwardaddr,
                python_binary_path, script
            )

    def _load_project_settings(self, project, project_root):
        sys.path.insert(0, project_root)
        try:
            settings_mod = __import__('mailserver_settings', ['settings'])
            reload(settings_mod)
            if os.path.dirname(settings_mod.__file__) == project_root and\
                isinstance(settings_mod.settings, list):
                logging.info('Loaded settings within project %s' % project)
                return settings_mod.settings
            return None
        except ImportError:
            return None
        finally:
            sys.path.remove(project_root)
