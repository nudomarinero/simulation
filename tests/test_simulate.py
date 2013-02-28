__author__ = 'jsm'

import unittest
#import getpass
from simulate import makems_command

class TestSimulate(unittest.TestCase):
    def setUp(self):
        #user = getpass.getuser()
        #default_path = "/data/scratch/%s/simulation"%user
        self.params = {"step_time":10,"path":"/data/scratch/montes/simulation"}
        self.params_obs = {"ra":"10:08:00.0","dec":"07.30.16.35","start_time":"2013/02/19/22:00:00","n_time":1800,
                      "sim_ms":"out.MS","name":"COSMOS_test"}
        self.params_hba = {"n_freq":14,"start_freq":"110e6","step_freq":"5e6","array":"HBA",
                      "antenna":"~weeren/scripts/ANTENNA_HBA","antenna_conf":"HBA_DUAL_INNER"}
        self.params_lba = {"n_freq":12,"start_freq":"15e6","step_freq":"5e6","array":"LBA",
              "antenna":"~weeren/scripts/ANTENNA_LBA","antenna_conf":"LBA_OUTER"}
        self.params.update({"sim_ms":"20130219_%(name)s_%(array)s.MS"%(self.params)})
        self.params.update({"full_sim_ms":self.params["path"]+"/"+self.params["sim_ms"]})


    def test_makems_command(self):
        """
        Tests the function makems_command
        """
        params = dict(self.params)
        params.update(self.params_obs)
        # Test HBA command
        params.update(self.params_hba)
        params.update({"sim_ms":"20130219_%(name)s_%(array)s.MS"%(params)})
        params.update({"full_sim_ms":params["path"]+"/"+params["sim_ms"]})
        command = makems_command(overwrite=True)
        commnad_hba = "cd /data/scratch/montes/simulation; makems " \
                      "/data/scratch/montes/simulation/makems_COSMOS_test_HBA.parset; " \
                       "makebeamtables antennaset=HBA_DUAL_INNER ms=out.MS overwrite=True"
        self.assertEqual(command,commnad_hba)
        # Test LBA command
        params.update(self.params_lba)
        params.update({"sim_ms":"20130219_%(name)s_%(array)s.MS"%(params)})
        params.update({"full_sim_ms":params["path"]+"/"+params["sim_ms"]})
        command = makems_command(overwrite=True)
        commnad_lba = "cd /data/scratch/montes/simulation; makems " \
                      "/data/scratch/montes/simulation/makems_COSMOS_test_LBA.parset; " \
                      "makebeamtables antennaset=LBA_DUAL_INNER ms=out.MS overwrite=True"
        self.assertEqual(command,commnad_lba)

if __name__ == '__main__':
    unittest.main()
