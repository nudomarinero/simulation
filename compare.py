"""
Selection of percentage of subbands and times affected by an A-team source.
"""
__author__ = 'jsm'
import pyrap.tables as tbl
import numpy
import argparse

# Location of the testing MS in lce012
msname_cyga = "/data/scratch/montes/simulation/COSMOS_20130219_sim_CygA.MS"
msname_source = "/data/scratch/montes/simulation/COSMOS_20130219_sim_source.MS"


class SimulationSet(object):
    """
    Class to store the data of a simulation.
    """
    # Indexes of the correlations
    corrind = {"XX": 0, "XY": 1, "YX": 2, "YY": 3}

    def __init__(self, msname):
        table = tbl.table(msname)
        self.model_data = table.getcol('MODEL_DATA')
        self.uvw = table.getcol('UVW')
        self.uvdist = numpy.sqrt(self.uvw[:,0]**2+self.uvw[:,1]**2)
        self.ntimes = len(numpy.unique(table.getcol('TIME')))
        self.nantennas = len(numpy.unique(table.getcol('ANTENNA1')))
        self.nbaselines = self.nantennas*(self.nantennas+1)/2
        self.nbaselines_cor = self.nantennas*(self.nantennas-1)/2
        self.uvorder = numpy.argsort(self.uvdist[0:self.nbaselines])
        shape_model_data = self.model_data.shape
        self.nchannels = shape_model_data[1]
        self.ncors = shape_model_data[2]
        self.amplitude = numpy.zeros((self.nchannels, self.ncors, self.ntimes, self.nbaselines_cor), dtype=float)
        for i in range(self.nchannels):
            for j in range(self.ncors):
                self.amplitude[i,j,:,:] = numpy.reshape(numpy.absolute(self.model_data[:,i,j]),
                                                (self.ntimes, self.nbaselines))[:,self.uvorder][:,self.nantennas:]


def threshold(SS,threshold=5.):
    """
    computes the fraction of measurements above the threshold for a given correlation.
    """
    #TODO: Merge with threshold_axis
    total_points = float(SS.ntimes*SS.nbaselines_cor)
    n_affected = numpy.zeros((SS.nchannels,SS.ncors), dtype=float)
    for i in range(SS.nchannels):
        for j in range(SS.ncors):
            n_affected[i,j] = numpy.count_nonzero(numpy.array((SS.amplitude[i,j,:,:] >= threshold), dtype=int))
    return n_affected/total_points


def threshold_axis(SS,threshold=5.,axis=1):
    """
    computes statistics for the measurements above the threshold for a given correlation
    with respect to an axis (by default axis 1 or time).
    It returns the whole measure.
    """
    if axis == 0:
        naxis = SS.nbaselines_cor
        total_points = float(SS.ntimes)
    else:
        naxis = SS.ntimes
        total_points = float(SS.nbaselines_cor)
    n_affected = numpy.zeros((SS.nchannels,SS.ncors,naxis), dtype=float)
    for i in range(SS.nchannels):
        for j in range(SS.ncors):
            n_affected[i,j,:] = numpy.sum(numpy.array((SS.amplitude[i,j,:,:] >= threshold), dtype = int), axis=axis)
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
    n_affected = numpy.zeros((SS_A.nchannels,SS_A.ncors), dtype=float)
    for i in range(SS_A.nchannels):
        for j in range(SS_A.ncors):
            n_affected[i,j] = numpy.count_nonzero(numpy.array(SS_A.amplitude[i,j,:,:] >=
                                                              SS_source.amplitude[i,j,:,:], dtype=int))
    return n_affected/total_points


#### Output ####
def print_threshold(a_ss,th):
    """
    Prints the percentage of affected data (maximum with respect to the time by default)
    for each channel using a threshold in the flux density
    """
    #TODO: Choose the statistics used
    per_affected = threshold_axis(a_ss,threshold=th)
    print "==================================="
    print "Flux density threshold: %f"%th
    for i in range(a_ss.nchannels):
        print "Freq: %2i XX: %6.2f%% YY: %6.2f%%"%(i, numpy.max(per_affected[i,0,:])*100.,
                                                   numpy.max(per_affected[i,3,:])*100.)


def print_comparison(a_ss,source_ss,level):
    """
    Prints the total percentage of affected data for each channel by comparing with
    the source observed.
    """
    #TODO: Add statistics with respect to time.
    per_compared = compare(a_ss,source_ss,level=level)
    print "==================================="
    print "Comparison with source. Level: %f"%level
    for i in range(a_ss.nchannels):
        print "Freq: %2i XX: %6.2f%% YY: %6.2f%%"%(i, per_compared[i,0]*100., per_compared[i,3]*100.)


def main(args):
    cyga = SimulationSet(args.ateam)
    for t in args.threshold:
        print_threshold(cyga,t)
    if args.source is not None:
        source = SimulationSet(args.source)
        for l in args.level:
            print_comparison(cyga,source,l)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Percentage of data affected by an A-team source')
    #parser.add_argument('-c','--cache',help='use a local cache to store and retrieve the data',action="store_true")
    parser.add_argument('ateam',metavar='ateam.MS',help='MS of the source')
    parser.add_argument('-t','--threshold',type=float,default=[5.],nargs='+',help='threshold(s)')
    parser.add_argument('-s','--source',metavar='source.MS',help='MS of target source')
    parser.add_argument('-l','--level',type=float,default=[0.05],nargs='+',
                        help='ratio(s) between the A-team data and source data')

    #args = parser.parse_args(["-s",msname_source,msname_cyga])
    args = parser.parse_args()

    main(args)



