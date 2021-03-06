#!/bin/env python
#
# AutoPyfactory batch plugin for Condor
#

from CondorBase import CondorBase 
from autopyfactory.apfexceptions import InvalidProxyFailure
from autopyfactory import jsd 


class CondorGrid(CondorBase):
   
    def __init__(self, apfqueue, config, section):

        qcl = config
        newqcl = qcl.clone().filterkeys('batchsubmit.condorgrid', 'batchsubmit.condorbase')
        super(CondorGrid, self).__init__(apfqueue, newqcl, section) 
        
        # ---- proxy management ------
        self.x509userproxy = None
        self.proxyfile = None
        self.proxylist = None
        
        # Allow a file to be explicitly set. 
        try:
            self.proxyfile = qcl.generic_get(self.apfqname, 'batchsubmit.condorgrid.proxyfile')
        
        except Exception as e:
            self.log.error("Caught exception: %s " % str(e)) 
        
        try:
            plist = qcl.generic_get(self.apfqname, 'batchsubmit.condorgrid.proxy')
            # This is alist of proxy profile names specified in proxy.conf
            # We will only attempt to derive proxy file path during submission
            if plist:
                self.proxylist = [x.strip() for x in plist.split(',')]
            self._getX509Proxy()
        
        except InvalidProxyFailure:
            self.log.error('Unable to get valid proxy file.')
            raise
        except Exception as e:
            self.log.error("Caught exception: %s " % str(e))
            raise

        self.log.debug('CondorGrid: Object initialized.')


    def _getX509Proxy(self):
        """
        uses authmanager to find out the path to the X509 file
        """
    
        self.log.debug("Determining proxy, if necessary. Profile: %s" % self.proxylist)
        if self.proxylist:
            self.x509userproxy = self.factory.authmanager.getProxyPath(self.proxylist)
        elif self.proxyfile:
            self.x509userproxy = self.proxyfile
        else:
            self.log.debug("No proxy profile defined.")


    def _addJSD(self):
        """   
        add things to the JSD object
        """   
        self.log.debug('CondorGrid.addJSD: Starting.') 
        self.JSD.add("universe", "grid")
        # -- proxy path --
        if self.x509userproxy:
            self.JSD.add("x509userproxy", "%s" % self.x509userproxy)
        else:
            self.log.warning('no x509 proxy found. Be sure one is set in defaults.')
        super(CondorGrid, self)._addJSD()
        self.log.debug('CondorGrid.addJSD: Leaving.')
    
