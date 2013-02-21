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

class MeasurementSet(object):
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


if __name__ == "__main__":
    cyga = MeasurementSet(msname_cyga)
    #source = MeasurementSet(msname_source)
    for i in range(cyga.nchannels):
        n_affectedxx = numpy.count_nonzero(numpy.array((cyga.amplitude[i,0,:,:] >= threshold),dtype = int))
        n_affectedyy = numpy.count_nonzero(numpy.array((cyga.amplitude[i,3,:,:] >= threshold),dtype = int))
        total_points = cyga.ntimes*cyga.nbaselines_cor
        print "Freq: %i XX:%f %% YY: %f %%"%(i,n_affectedxx/total_points,n_affectedyy/total_points)

