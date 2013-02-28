

LOFAR simulation software
=========================

The software package is composed at the moment of two Python scripts, 
one to simulate the data (simulate.py) and the other to compare 
simulations (compare.py). The usage of the programs is displayed 
by calling them with the option -h or --help.

The first step to simulate the effect of one source (usually an A-Team) 
on our observation is to create a mock measurement set (MS) with the 
information of the observation (using makems). Later the calibration 
tables of the observing modes have to be updated into the MS (using 
makebeamtables). Then it is possible to simulate using BBS the effect 
of a model source on the data. The commands and parsets needed for all 
those steps are generated with the command "simulate.py".

The second step is to check what is the effect of the source on the 
target field. This effect can be quantified in two ways. The first is 
to check the amplitude of the source on the target field. All the 
data points that present flux from the source above a certain threshold 
are considered as affected and the final percentage of the data 
affected is shown. The second way is to compare the flux of the 
interfering source with the flux of a central source in the target
field (using a scaling factor called "level"). If the flux of the 
source is 'level' times higher than the flux of the central source 
in a data point this point is considered to be affected by the source. 

Dependencies and location
-------------------------

The software depends on several Python modules that are already
installed in the LOFAR clusters. 

At the moment it can be found in the directory ~montes/xmm/simulations.
It is a git repository so you can obtain a copy using:
git clone ~montes/xmm/simulations

Usage of simulate.py
--------------------

To simulate an observation, the position, observation time, and
length of the observation, of the target must be specified with the 
options --ra, --dec, --time and --n-time (in number of steps of 10 
seconds) respectively. It is also interesting to specify the name of the
field simulated using the option --name. The option --overwrite may be
needed to allow the overwriting of parset and MS files. The sources to
be simulated can be specified after the option --source. Currently, it
is possible to specify CygA, CasA4, TauA, VirA4, HydraA. It is also
possible to use CasA and VirA but the simulation can be very slow. The
sources 3C53 and 3C237 are also included. The data are store in 
/data/scratch/<user_name>/simulation/ by default but an alternative
location can be specified with the option --path. Finally, the script
generates by default the files for an HBA observation, if the option
--lba is specified, an LBA observation is simulated.

With the current version of the program, the working directory and the
necessary parsets are created but the commands are only displayed on
screen and must be executed by the user.

Example

python ~montes/xmm/simulations/simulate.py --ra 10:47:00.0 \
--dec 58.05.00.0 --time 2013/03/03/19:00:00 --n-time 3600 \
--name Lockman_Hole_field --source CasA4 CygA TauA VirA4 \
--overwrite --lba

TODO:
  * Allow the direct execution of the commands by the script
  * Allow different antenna configurations. At the moment, the default
 HBA configuration is HBA_DUAL_INNER and the default LBA configuration
 is LBA_OUTER.
  * Test the option --skymodel

Usage of compare.py
-------------------

The effect of an A-team source can be assessed using this script. The
simulation file (that created with simulate.py) of an A-Team source must
be entered. The default threshold to consider that a source is affecting
a data point is 5 Jy. A different threshold or set of threshold can be
specified with the option -t or --threshold. The output is the median 
value of the percentage of data points affected with respect to the time
for the XX and YY croscorrelations.

Example

python  ~montes/xmm/simulations/compare.py \
/data/scratch/montes/simulation/20130303_Lockman_Hole_field_LBA_CygA.MS \
-t 2.5 5. 10. -f "median"


It is also possible to enter the simulated MS of the central source
using the option -s or --source. If this is entered, the comparison
levels can be specified with the option -l or --level. The percentages
displayed are with respect to the points for which the flux of source is
stronger than "level" times the flux of the central source.

Example

python  ~montes/xmm/simulations/compare.py \
/data/scratch/montes/simulation/COSMOS_20130219_sim_CygA.MS \
-s/data/scratch/montes/simulation/COSMOS_20130219_sim_source.MS \
-l 0.01 0.1 0.5 1. -f "median"

The options -l plus -s can be used together mixed with the options -t.

NOTE:
Due to a bug in the Python module "argparse", if the options -t or -l
are used, they can not be followed by the name of the A-Team source.
They can be followed by any other option or, the name of the A-Team
source can be placed at the beginning, just after compare.py.

TODO:
  * Allow the simultaneous comparison of several A-Team sources.



