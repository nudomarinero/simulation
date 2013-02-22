"""
Selection of percentage of subbands and times affected by an A-team source.
 The first version will just apply a threshold (i.e. 5 Jy) to select data points
 affected by the A-team source.
"""
__author__ = 'jsm'
import pyrap.tables as tbl
import numpy


# Location of the testing MS in lce012
msname_cyga = "/data/scratch/montes/simulation/COSMOS_20130219_sim_CygA.MS"
msname_source = "/data/scratch/montes/simulation/COSMOS_20130219_sim_source.MS"

threshold = 5.

class SimulationSet(object):
    """

    """
    # Indexes of the correlations
    corrind = {"XX":0,"XY":1,"YX":2,"YY":3}
    def __init__(self,msname):
        self.table = tbl.table(msname)
        self.model_data = self.table.getcol('MODEL_DATA')
        self.uvw = self.table.getcol('UVW')
        self.uvdist = numpy.sqrt(self.uvw[:,0]**2+self.uvw[:,1]**2)
        self.ntimes = len(numpy.unique(self.table.getcol('TIME')))
        self.nantennas = len(numpy.unique(self.table.getcol('ANTENNA1')))
        self.nbaselines = self.nantennas**2/2
        self.nbaselines_cor = self.nantennas*(self.nantennas-1)/2
        self.uvorder = numpy.argsort(self.uvdist[0:self.nbaselines])
        shape_model_data = self.model_data.shape
        self.nchannels = shape_model_data[1]
        self.ncors = shape_model_data[2]
        self.amplitude = numpy.zeros((self.nchannels,self.ncors,self.ntimes,self.nbaselines_cor),dtype=float)
        for i in range(self.nchannels):
            for j in range(self.ncors):
                self.amplitude[i,j,:,:] = numpy.reshape(numpy.absolute(self.model_data[:,i,j]),
                                                        (self.ntimes,self.nbaselines))[:,self.uvorder][:,self.nantennas:]


def threshold(SS,threshold=5.):
    """
    computes the number of measurements above the threshold for a given correlation.
    """
    total_points = float(SS.ntimes*SS.nbaselines_cor)
    n_affected = numpy.zeros((SS.nchannels,SS.ncors),dtype=float)
    for i in range(SS.nchannels):
        for j in range(SS.ncors):
            n_affected[i,j] = numpy.count_nonzero(numpy.array((SS.amplitude[i,j,:,:] >= threshold),dtype = int))
    return n_affected/total_points


def compare(SS_A,SS_source,level=0.01):
    """
    computes the number of measurements where the first source has a value "level" times higher
    than the second source.
    """
    # Check if the two simulations are compatible
    assert SS_A.ntimes == SS_source.ntimes
    assert SS_A.nbaselines_cor == SS_source.nbaselines_cor
    assert SS_A.nchannels == SS_source.nchannels
    assert SS_A.ncors == SS_source.ncors

    total_points = float(SS_A.ntimes*SS_A.nbaselines_cor)
    n_affected = numpy.zeros((SS_A.nchannels,SS_A.ncors),dtype=float)
    for i in range(SS_A.nchannels):
        for j in range(SS_A.ncors):
            n_affected[i,j] = numpy.count_nonzero(numpy.array(SS_A.amplitude[i,j,:,:] >= SS_source.amplitude[i,j,:,:])
                ,dtype = int))
    return n_affected/total_points


if __name__ == "__main__":
    cyga = SimulationSet(msname_cyga)
    source = SimulationSet(msname_source)
    per_affected = threshold(cyga)
    for i in range(cyga.nchannels):
        print "Freq: %2i XX: %6.2f%% YY: %6.2f%%"%(i,per_affected[i,0]*100.,per_affected[i,3]*100.)
    per_compared = compare(cyga,source,level=0.1)
    for i in range(cyga.nchannels):
        print "Freq: %2i XX: %6.2f%% YY: %6.2f%%"%(i,per_compared[i,0]*100.,per_compared[i,3]*100.)

