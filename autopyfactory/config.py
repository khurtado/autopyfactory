#! /usr/bin/env python

import logging
import logging.handlers


# FIXME: many of these import are not needed. They are legacy...
from autopyfactory.apfexceptions import FactoryConfigurationFailure, PandaStatusFailure, ConfigFailure
from autopyfactory.apfexceptions import CondorVersionFailure, CondorStatusFailure
from autopyfactory.configloader import Config, ConfigManager
from autopyfactory.cleanlogs import CleanLogs
from autopyfactory.logserver import LogServer
from autopyfactory.pluginmanager import PluginManager
from autopyfactory.interfaces import _thread


class ConfigHandler(_thread):

    def __init__(self, factory):

        _thread.__init__(self)
        self.log = logging.getLogger('autopyfactory.confighandler')

        self.factory = factory
        self.reconfig = factory.fcl.generic_get('Factory', 'config.reconfig', 'getboolean', default_value=False)
        self.interval = None
        if self.reconfig:
            self.interval = factory.fcl.generic_get('Factory','config.reconfig.interval', 'getint', default_value=3600) 


    def setconfig(self):
        # NOTE:
        # for now, we reconfig both or none
        if self.reconfig:
            self._startthread()
        else:
            # at least set configuration once
            self._run()


    def _startthread(self):
        self.factory.threadsregistry.add("core", self)
        self._thread_loop_interval = self.interval
        self.start()


    def _run(self):
        # order matters here: 
        # first reconfig AuthManager, then APFQueuesManager
        try:
            self._run_auth()
        except:
            self.log.error('seting configuration for AuthManager failed. Will not proceed with threads configuration.')
            return
        try:
            self._run_queues()
        except:
            self.log.error('seting configuration for queues failed.')


    # NOTE
    # code is duplicated for methods _run_XYZ() and getXYZConfig()
    # but for now is OK

    def _run_auth(self):
        newconfig = self.getAuthConfig()
        self.factory.authmanager.reconfig(newconfig)
        self.factory.authmanager.startHandlers()
        self.log.debug("Completed creation of %d auth handlers." % len(self.factory.authmanager.handlers))


    def _run_queues(self):
        newconfig = self.getQueuesConfig()
        self.factory.apfqueuesmanager.reconfig(newconfig)
        self.factory.apfqueuesmanager.startAPFQueues() #starts all threads


    def getAuthConfig(self):
        """
        get updated configuration from the Factory Config/Auth plugins
        """
        newconfig = Config()
        for config_plugin in self.factory.auth_config_plugins:
            tmpconfig = config_plugin.getConfig()
            newconfig.merge(tmpconfig)
        return newconfig


    def getQueuesConfig(self):
        """
        get updated configuration from the Factory Config/Queues plugins
        """
        newconfig = Config()
        for config_plugin in self.factory.queues_config_plugins:
            tmpconfig = config_plugin.getConfig()
            newconfig.merge(tmpconfig)
        return newconfig