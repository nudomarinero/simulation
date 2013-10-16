"""
Simulation of the observation
"""
from __future__ import print_function
__author__ = 'jsm'
import argparse
#import subprocess
import getpass
import os

############## Default configuration

user = getpass.getuser()
#Default directory
default_path = "/data/scratch/%s/simulation"%user

template_makebeam = """
NParts=0
NBands=1
NFrequencies=%(n_freq)i
StartFreq=%(start_freq)s
StepFreq=%(step_freq)s
StartTime=%(start_time)s
StepTime=%(step_time)i
NTimes=%(n_time)i
RightAscension=%(ra)s
Declination=%(dec)s
TileSizeFreq=8
TileSizeRest=10
WriteAutoCorr=T
AntennaTableName=%(antenna)s
MSName=%(sim_ms)s
VDSPath=.
"""

template_predict = """
Strategy.InputColumn = DATA
Strategy.ChunkSize = 100
Strategy.UseSolver = F
Strategy.Steps = [predict]

Step.predict.Model.Sources         = [%(source_patch)s]
Step.predict.Model.Gain.Enable     = F
Step.predict.Model.Cache.Enable     = T
Step.predict.Operation             = PREDICT
Step.predict.Output.Column         = MODEL_DATA
Step.predict.Model.Beam.Enable     = True
Step.predict.Model.Beam.UseChannelFreq     = T
"""

params = {"step_time":10,"path":default_path}
params_obs = {"ra":"10:08:00.0","dec":"07.30.16.35","start_time":"2013/02/19/22:00:00","n_time":1800,
              "sim_ms":"out.MS","name":"COSMOS_test"}
params_hba = {"n_freq":14,"start_freq":"110e6","step_freq":"5e6","array":"HBA",
              "antenna":"~weeren/scripts/ANTENNA_HBA","antenna_conf":"HBA_DUAL_INNER"}
params_lba = {"n_freq":12,"start_freq":"15e6","step_freq":"5e6","array":"LBA",
              "antenna":"~weeren/scripts/ANTENNA_LBA","antenna_conf":"LBA_OUTER"}

params.update(params_obs) # Set of default values for an observation

source_model = {"CygA":"~montes/xmm/3C237_demix.skymodel",
                "CasA":"~montes/xmm/3C237_demix.skymodel",
                "CasA4":"~weeren/scripts/Ateam_LBA_CC.skymodel",
                "HydraA":"/opt/lofar/share/pipeline/skymodels/Ateam_LBA_CC.skymodel",
                "VirA":"/opt/lofar/share/pipeline/skymodels/Ateam_LBA_CC.skymodel",
                "VirA4":"/opt/lofar/share/pipeline/skymodels/Ateam_LBA_CC.skymodel",
                "TauA":"/opt/lofar/share/pipeline/skymodels/Ateam_LBA_CC.skymodel",
                "HerA":"/opt/lofar/share/pipeline/skymodels/Ateam_LBA_CC.skymodel",
                "3C295":"/globaldata/COOKBOOK/Models/3C295_TWO_MSSS.skymodel",
                "3C48":"/globaldata/COOKBOOK/Models/3C48_MSSS.skymodel",
                "3C196":"/globaldata/COOKBOOK/Models/3C196_MSSS.skymodel",
                "3C237":"~montes/xmm/3C237_demix.skymodel",
                "3C53":"~montes/xmm/3C53_CasA_demix.skymodel"}
# Names of the models within the file
source_name = {"CygA":"CygA_LBAHR",
               "CasA4":"CasA_4_patch",
               "VirA4":"VirA_4_patch",
               "CasA":"CasA_LBAHR"}
source_params = {}

#Antenna configurations 2013-04-17
antenna_confs = ["LBA_INNER","LBA_OUTER","LBA_SPARSE_EVEN","LBA_SPARSE_ODD","LBA_X",
                 "LBA_Y","HBA_ZERO","HBA_ONE","HBA_DUAL","HBA_JOINED","HBA_ZERO_INNER",
                 "HBA_ONE_INNER","HBA_DUAL_INNER","HBA_JOINED_INNER"]
antenna_ba = {ant:ant.split("_")[0] for ant in antenna_confs}


##############

## Mock MS commands
# This can be executed only after updating "params"

def makems_file(overwrite=True):
    """
    Create makems parset according to the params.
    """
    if (not os.path.exists(params["makems_parset"])) or overwrite:
        outfile = file(params["makems_parset"],"w")
        outfile.write(template_makebeam%params)
        outfile.close()
    else:
        print("# File %(makems_parset)s already exists;"%params)
        #raise IOError("File makems parset already exists")


def makems_command(overwrite=True):
    """
    Command to create the base MS for the simulation using the makems parset.
    """
    if (not os.path.exists(params["full_sim_ms"])) or overwrite:
        command = "cd %(path)s; makems %(makems_parset)s; " \
              "makebeamtables antennaset=%(antenna_conf)s ms=%(sim_ms)s overwrite=True"%params
    else:
        command = ""
    return command


## Simulation commands
# This can be executed only after creating the "source_params"

def simulation_file(overwrite=True):
    if (not os.path.exists(source_params["full_sim_parset"])) or overwrite:
        outfile = file(source_params["full_sim_parset"],"w")
        outfile.write(template_predict%source_params)
        outfile.close()
    else:
        print("# File %(sim_parset)s already exists;"%source_params)
        #raise IOError("File predict parset already exists")


def copy_ms_command(overwrite=True):
    """
    Command to make a copy of the mock MS to simulate the data.
    """
    if (not os.path.exists(source_params["full_sim_name"])) or overwrite:
        command = "cp -r %s %s"%(params["full_sim_ms"],source_params["full_sim_name"])
    else:
        command = ""
    return command


def simulation_command():
    command = "cd %(path)s; (date; calibrate-stand-alone -f %(full_sim_name)s %(sim_parset)s " \
              "%(skymodel)s; date) | tee %(logfile)s"%source_params
    return command


## Input auxiliary functions

def update_obs_params(args):
    """
    Update the params file with the observation parameters
    """
    # Update the antenna configuration
    if args.lba:
        params.update(params_lba)
    else:
        params.update(params_hba)
    # Update the observation data
    d = {"ra":args.ra,"dec":args.dec,"start_time":args.time,"n_time":args.n_time}
    # Get name
    date_string = "".join(args.time.split("/")[0:3])
    if args.name is None:
        d.update({"name":date_string}) # TODO: Upgrade default naming scheme
    else:
        d.update({"name":args.name})
    # Get base simulation output name
    d.update({"sim_ms":"%s_%s_%s.MS"%(date_string,d["name"],params["array"])})
    d.update({"full_sim_ms":params["path"]+"/"+d["sim_ms"]})
    # TODO: Add the update of the antenna configuration
    params.update(d)
    # Makems parset name
    params.update({"makems_parset":"%(path)s/makems_%(name)s_%(array)s.parset"%params})


def update_source_params(source,default_skymodel):
    """
    Create the dictionary with the parameters for the simulated source(s)
    """
    source_params.update({"sim_name":params["sim_ms"].split(".")[0]+"_%s.MS"%source,
                          "skymodel":source_model.get(source,default_skymodel),
                          "source_patch":source_name.get(source,source),
                          "source":source,
                          "logfile":"log_%s_%s.txt"%(params["name"],source),
                          "sim_parset":"predict_%s.parset"%(source)})
    source_params.update({"full_sim_name":"%(path)s/%(sim_name)s"%source_params,
                          "full_sim_parset":"%(path)s/%(sim_parset)s"%source_params})


def create_path(path):
    """
    Creates a path if it does not exist
    """
    if not os.path.exists(path):
        os.makedirs(path)


## Command line parser

def main(args):
    params.update({"path":args.path})
    source_params.update({"path":args.path})
    if (args.antenna_conf is not None):
        if (args.antenna_conf not in antenna_confs):
            print("# WARNING: Possible problem with the antenna configuration: "
                  "#  Undefined configuration.")
        if ((args.antenna_conf.split("_")[0] == "LBA")and(not args.lba)):
            print("# WARNING: Possible problem with the antenna configuration: "
                  "#  HBA configuration in LBA simulation.")
        if ((args.antenna_conf.split("_")[0] == "HBA")and(args.lba)):
            print("# WARNING: Possible problem with the antenna configuration: "
                  "#  LBA configuration in HBA simulation.")
    update_obs_params(args)
    overwrite = args.overwrite
    # Create simulation path
    if not args.dry_run:
        create_path(params["path"])
    # Create simulation parset
    if not args.dry_run:
        makems_file(overwrite)
    else:
        print("# Create makems file %(makems_parset)s;"%params)
    # Create base simulation
    print(makems_command(overwrite))
    if args.sources is not None:
        for s in args.sources:
            update_source_params(s,args.sky_model)
            # Copy dataset
            print(copy_ms_command(overwrite))
            # Create simulation parset
            if not args.dry_run:
                simulation_file(overwrite)
            else:
                print("# Create simulation parset file %(sim_parset)s;"%source_params)
            # Simulate data
            print(simulation_command())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Simulation of the effect of one source in one field')
    parser.add_argument('--ra',required=True,help='right ascension of the field')
    parser.add_argument('--dec',required=True,help='declination of the field')
    parser.add_argument('--time',required=True,help='start date and time of the observation')
    parser.add_argument('--n-time',type=int,default=1800,help='duration of the observation in multiples '
                        'of 10 seconds. The default value is 1800 (5 hours)')
    parser.add_argument('--name',help='name of the observed field and prefix of the output')
    parser.add_argument('--sources',nargs='*',help='name of the source(s) to simulate. There are default '
                        'skymodels for CygA, CasA (long run), CasA4, HydraA, HerA, TauA, VirA, 3C297 or 3C53.')
    parser.add_argument('--sky-model',help='skymodel of the source(s) to simulate that do not have '
                        'a skymodel by default')
    parser.add_argument('--path',default=default_path,help='path to store the measurement sets of the '
                        'simulation. By default %s'%default_path)
    parser.add_argument('--overwrite',action="store_true",default=False,help='overwrite existing files')
    parser.add_argument('--lba',action="store_true",default=False,help='LBA simulation (HBA by default)')
    parser.add_argument('--antenna-conf',help='Antenna configuration (optional). The default antenna '
                                              'configurations are HBA_DUAL_INNER for HBA and LBA_OUTER '
                                              'for LBA.')
    parser.add_argument('--dry-run',action="store_true",default=False,help='Only show information. '
                                                                           'Do not actually run anything.')
    # Add option for dry run ???
    #args = parser.parse_args(["-s",msname_source,msname_cyga])
    args = parser.parse_args()

    main(args)
