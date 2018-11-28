# don't actually run this! It will destory things!

# example of querying the database for fireworks, copying the spec, changing it, then updating the entries.
exit()
from fireworks import LaunchPad
lpad = LaunchPad.auto_load()
bad_fws = list(lpad.db.fireworks.find({"name": {"$regex": "phonon"}, "state": {"$regex" : "PAUSED"}}))
print(len(bad_fws))
for i in range(len(bad_fws)):
    fw = bad_fws[i]
    fid = fw['fw_id']
    from copy import deepcopy
    new_spec = deepcopy(fw['spec'])
    new_spec['_tasks'][1]['supercell_matrix'] = new_spec['_tasks'][1]['supercell_matrix'][0]
    lpad.db.fireworks.find_one_and_update({'fw_id': fid}, {"$set": {'spec': new_spec}})


