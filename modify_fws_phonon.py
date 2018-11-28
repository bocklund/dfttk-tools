DRY_RUN = False

if DRY_RUN:
    print('Dry run, will not change')

import numpy as np
from copy import deepcopy

# example of querying the database for fireworks, copying the spec, changing it, then updating the entries.
from fireworks import LaunchPad
lpad = LaunchPad.auto_load()

# these need to be set to index 3 and added to index 4, respectively
run_vasp_custodian_no_validate_dict = {'_fw_name': '{{dfttk.ftasks.RunVaspCustodianNoValidate}}', 'auto_npar': '>>auto_npar<<', 'gzip_output': False, 'vasp_cmd': '>>vasp_cmd<<'}
fix_vasprun_task_dict = {'_fw_name': 'PyTask', 'args': ['vasprun.xml'], 'func': 'dfttk.vasprun_fix.fix_vasprun'}

bad_fws = list(lpad.db.fireworks.find({"name": {"$regex": "phonon"}, "$or":[{"state": "READY"}, {"state": "WAITING"}]}))

print(len(bad_fws), " fireworks")
for i in range(len(bad_fws)):
    fw = bad_fws[i]
    fid = fw['fw_id']
    new_spec = fw['spec']
    new_spec['_tasks'][3] = run_vasp_custodian_no_validate_dict
    new_spec['_tasks'].insert(4, fix_vasprun_task_dict)
    if DRY_RUN:
        pass
    else:
        lpad.db.fireworks.find_one_and_update({'fw_id': fid}, {"$set": {'spec': new_spec}})

if DRY_RUN:
    print('Dry run, did not change')
