'''
Created on May 22, 2012

@author: vencax
'''
import os
import logging
import time
import threading
import re
import sys

class Settings(object):
    """
    Loads and polls setting folder.
    """

    def __init__(self, projects_root, path_to_project_root, path_to_python,
                 poll_interval, lock):
        """
        @param projects_root: path where all django web projects are located.
        @param path_to_project_root: path to specific project within
        projects_root/<specific proj>/ subdirectory.
        @param path_to_python: path to python binary which shall be  used to
        run email processing script. The absolute path means run global python binary.
        The relative is path within project subtree - virtualenv binary.
        """
        self._projects_root = projects_root
        if not os.path.exists(self._projects_root):
            raise AttributeError('project_root %s not exists' %\
                                 self._projects_root)
        self._path_to_project_root = path_to_project_root
        self._path_to_python = path_to_python
        self._setting_poll_interval = poll_interval
        self._settingslock = lock

    def load(self):
        settings = {}
        for project in os.listdir(self._projects_root):
            project_root = os.path.join(self._projects_root,
                                    project, self._path_to_project_root)
            
            proj_sett = self._load_project_settings(project, project_root)
            self._add_project_settings(proj_sett, settings, 
                                       project, project_root)
        self._settingslock.acquire()
        self.info = settings
        self._settingslock.release()
        logging.info('Settings loaded ...')

    def run(self):
        self._running = True
        threading.Thread(target=self._settings_poll_thread_func,
                         name='settings_thread').start()
                         
    def stop(self):
        self._running = False
    
    # -------------------------- privates -------------------------------------
        
    def _add_project_settings(self, proj_settings, settingsmap, 
                              project, project_root):
        if not proj_settings:
            return
        for domainInfo in proj_settings:
            try:
                domain, mapping, forwardaddr = domainInfo
                mappinginfo = []
                for regex, command in mapping.items():
                    mappinginfo.append((re.compile(regex), command))
                
                python_binary_path = self._path_to_python
                if not self._path_to_python.startswith('/'):    
                    python_binary_path = os.path.join(self._projects_root,
                                project, self._path_to_python)
                    
                script = os.path.join(project_root, 'manage.py')
                settingsmap[domain] = (mappinginfo, forwardaddr, 
                                       python_binary_path, script)
            except Exception:
                pass

    def _load_project_settings(self, project, project_root):        
        sys.path.insert(0, project_root)
        try:
            settings_mod = __import__('%s.mailserver_settings' % project,
                              globals(), locals(), ['settings'])
            if isinstance(settings_mod.settings, list):
                return settings_mod.settings
        except ImportError, e:
            logging.exception(e)
        finally:
            sys.path.remove(project_root)

    def _settings_poll_thread_func(self):
        while(self._running):
            time.sleep(self._setting_poll_interval)
            self.load()