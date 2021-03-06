#!/bin/env python
#
# AutoPyfactory batch plugin for Condor
#

from CondorCE import CondorCE 
import autopyfactory.utils as utils
from autopyfactory import jsd 


class CondorCREAM(CondorCE):
    id = 'condorcream'
    """
    This class is expected to have separate instances for each PandaQueue object. 
    """
   
    def __init__(self, apfqueue, config, section):

        qcl = config
        newqcl = qcl.clone().filterkeys('batchsubmit.condorcream', 'batchsubmit.condorce')
        super(CondorCREAM, self).__init__(apfqueue, newqcl, section) 
        try:
            self.gridresource = qcl.generic_get(self.apfqname, 'batchsubmit.condorcream.gridresource') 
            self.webservice = qcl.generic_get(self.apfqname, 'batchsubmit.condorcream.webservice')
            self.creamport = qcl.generic_get(self.apfqname, 'batchsubmit.condorcream.port', 'getint')
            self.creambatch = qcl.generic_get(self.apfqname, 'batchsubmit.condorcream.batch')
            self.queue = qcl.generic_get(self.apfqname, 'batchsubmit.condorcream.queue')
        
        except Exception as e:
            self.log.error("Caught exception: %s " % str(e))
            raise
        
        self.log.info('CondorCREAM: Object initialized.')

          
    def _addJSD(self):
        """
        add things to the JSD object
        """
        self.log.debug('CondorCREAM.addJSD: Starting.')
        # if variable webservice, for example, has a value, 
        # then we can assume the grid resource line is meant to be built from pieces.
        # Otherwise, we will assume its entire value comes from gridresource variable. 
        if self.webservice:
                self.JSD.add('grid_resource', 'cream %s:%d/ce-cream/services/CREAM2 %s %s' % (self.webservice, self.creamport, self.creambatch, self.queue))
        else:
                self.JSD.add('grid_resource', 'cream %s' %self.gridresource)
        super(CondorCREAM, self)._addJSD() 
        self.log.debug('CondorCREAM.addJSD: Leaving.')

