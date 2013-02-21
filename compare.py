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

# Indexes of the correlations
corrind = {"XX":0,"XY":1,"YX":2,"YY":3}

cyga = tbl.table(msname_cyga)
#source = tbl.table(msname_source)

model_data_cyga = cyga.getcol('MODEL_DATA')
#model_data_source = source.getcol('MODEL_DATA')

uvw = cyga.getcol('UVW')
uvdist = numpy.sqrt(uvw[:,0]**2+uvw[:,1]**2)
# TODO: Infer 1770
uvorder = numpy.argsort(uvdist[0:1770])

# TODO: Infer the number of antennas
amplitude_cyga_xx = numpy.reshape(numpy.absolute(model_data_cyga[:,0,0]), (1800,1770))[:,uvorder][:,59:]
#amplitude_source_xx = numpy.reshape(numpy.absolute(model_data_source[:,0,0]), (1800,1770))[:,uvorder][:,59:]

amplitude_cyga_yy = numpy.reshape(numpy.absolute(model_data_cyga[:,0,3]), (1800,1770))[:,uvorder][:,59:]
#amplitude_source_yy = numpy.reshape(numpy.absolute(model_data_source[:,0,3]), (1800,1770))[:,uvorder][:,59:]

#rel_xx = numpy.log10(amplitude_cyga_xx/amplitude_source_xx)
#rel_yy = numpy.log10(amplitude_cyga_yy/amplitude_source_yy)

nchan = 14

for i in range(nchan):
    amplitude_cyga_xx = numpy.reshape(numpy.absolute(model_data_cyga[:,i,0]), (1800,1770))[:,uvorder][:,59:]
    amplitude_cyga_yy = numpy.reshape(numpy.absolute(model_data_cyga[:,i,3]), (1800,1770))[:,uvorder][:,59:]

    n_affectedxx = numpy.count_nonzero(numpy.array((amplitude_cyga_xx >= threshold),dtype = int))
    n_affectedyy = numpy.count_nonzero(numpy.array((amplitude_cyga_yy >= threshold),dtype = int))

    print "Freq: %i XX:%f %% YY: %f %%"%(i,n_affectedxx/1800./1711.,n_affectedyy/1800./1711.)
