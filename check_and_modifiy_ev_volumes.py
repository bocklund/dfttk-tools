# sometimes the EV curve range on the static calculations are too large, and there are calculation failures. 
# this code will take an input tag, plot the EV curve 

TAG = 'my-tag-here'

db_username = 'READONLYUSER'
db_password = 'oijasodlkjfa'
db_uri = 'mongodb://192.168.1.1:27017'

FW_ID_TO_CHANGE = 777 # FW_ID of the firework to change
NEW_SCALE_FACTOR = 0.93

DRY_RUN = True  # If True, just show the plot and exit.

### SCRIPT:
from pymongo import MongoClient

cli = MongoClient(db_uri)
db = cli.results
db.authenticate(name=db_username, password=db_password)


# for IPython or Jupyter:
# %matplotlib inline
import matplotlib.pyplot as plt
e, v = zip(*[(x['output']['energy_per_atom'], x['output']['structure']['lattice']['volume']) for  x in db.tasks.find({'metadata.tag': TAG})])

print("Check which result is missing or what doesn't make sense:")
plt.scatter(v,e)

if DRY_RUN:
    exit()

from fireworks import LaunchPad
lpad = LaunchPad.auto_load()
lpad.db.fireworks.update_one({"fw_id": FW_ID_TO_CHANGE}, {'$set': {'spec._tasks.2.scale_factor': NEW_SCALE_FACTOR}})


