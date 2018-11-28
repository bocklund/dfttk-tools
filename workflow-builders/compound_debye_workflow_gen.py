##############
# User Input #
##############

# this script does not substitute, just takes a structure and the data and submits it.

DRY_RUN = False  # Don't submit the workflows
VERBOSE = True   # Turn on printing of substitutions

# Filename of the template structure to use, usually a dilute or SQS structure
TEMPLATE_STRUCTURE_FILENAME = 'structures/compounds/NiMg2.C16.POSCAR'

# sublattice configuration of the template structure.
# This will be substitued exactly, this does not need to be sorted,
# however the individual configurations to build should be sorted.
TEMPLATE_SUBLATTICE_CONFIGURATION = [['Ni'], ['Mg']]
TEMPLATE_SUBLATTICE_OCCUPANCIES = [[1.0], [1.0]]
SUBL_SITE_RATIOS = [1.0, 2.0]

PHASE_NAME = 'NIMG2'

##########
# SCRIPT #
##########

# Should not need to edit below this line.

from pymatgen import Structure
from fireworks import LaunchPad
from dfttk import get_wf_gibbs
from dfttk.structure_builders.substitutions import substitute_configuration_with_metadata
from collections import defaultdict

density_defaults = defaultdict(lambda: 1)
workflows = []

struct = Structure.from_file(TEMPLATE_STRUCTURE_FILENAME)

x_, meta = substitute_configuration_with_metadata(struct, TEMPLATE_SUBLATTICE_CONFIGURATION, TEMPLATE_SUBLATTICE_CONFIGURATION, density_defaults, TEMPLATE_SUBLATTICE_OCCUPANCIES, PHASE_NAME, SUBL_SITE_RATIOS )
if VERBOSE:
    print("PHASE: {}    CONFIGURATION: {}    OCCUPANCIES: {}    STRUCTURE: {}".format(PHASE_NAME, TEMPLATE_SUBLATTICE_CONFIGURATION, TEMPLATE_SUBLATTICE_OCCUPANCIES, struct.composition.hill_formula))
workflows.append(get_wf_gibbs(struct, deformation_fraction=(-0.05,0.15), phonon=False, num_deformations=11, t_max=2000, metadata=meta))


################################################################################
# Load everything in the LaunchPad
################################################################################

if VERBOSE:
    print("{} workflows.".format(len(workflows)))

if DRY_RUN:
    exit()

if VERBOSE:
    print('Adding workflows to LaunchPad')

lpad = LaunchPad.auto_load()

for workflow in workflows:
    lpad.add_wf(workflow)
