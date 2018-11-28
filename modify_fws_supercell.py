DRY_RUN = True

if DRY_RUN:
    print('Dry run, will not change')

import numpy as np
from copy import deepcopy

# example of querying the database for fireworks, copying the spec, changing it, then updating the entries.
from fireworks import LaunchPad
lpad = LaunchPad.auto_load()
bad_fws = list(lpad.db.fireworks.find({"name": {"$regex": "phonon"}}))
print(len(bad_fws))
for i in range(len(bad_fws)):
    fw = bad_fws[i]
    fid = fw['fw_id']
    make_change = False
    for task_i in (1, -1):
        sc_mat = np.array(fw['spec']['_tasks'][task_i]['supercell_matrix'])
        if sc_mat.shape == (1, 3, 3):
            make_change = True
            new_spec = deepcopy(fw['spec'])
            new_spec['_tasks'][task_i]['supercell_matrix'] = new_spec['_tasks'][task_i]['supercell_matrix'][0]
    if make_change:
        print('Changing FW id {}'.format(fid))
        if DRY_RUN:
            pass
        else:
            lpad.db.fireworks.find_one_and_update({'fw_id': fid}, {"$set": {'spec': new_spec}})
    else:
        print('Good FW id {}'.format(fid))

if DRY_RUN:
    print('Dry run, did not change')
