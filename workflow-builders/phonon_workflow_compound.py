##############
# User Input #
##############

DRY_RUN = False  # Don't submit the workflows
VERBOSE = True   # Turn on printing of substitutions

# Filename of the template structure to use, usually a dilute or SQS structure
TEMPLATE_STRUCTURE_FILENAME = 'structures/compounds/NITI2.NiTi2.POSCAR'

TEMPLATE_SUBLATTICE_CONFIGURATION = [['NI'], ['TI']]
TEMPLATE_SUBLATTICE_OCCUPANCIES = [[1.0], [1.0]]
SUBL_SITE_RATIOS = [1.0, 2.0]

# phonon supercell matrix
SUPERCELL_MATRIX = [[1,0,0],[0,1,0],[0,0,1]]

PHASE_NAME = 'NITI2'


##########
# SCRIPT #
##########

# Should not need to edit below this line.

from pymatgen import Structure
from fireworks import LaunchPad
from dfttk import get_wf_gibbs
from dfttk.structure_builders.substitutions import substitute_configuration_with_metadata

workflows = []

temp_struct = Structure.from_file(TEMPLATE_STRUCTURE_FILENAME)

struct = temp_struct
meta = {'phase_name': PHASE_NAME, 'sublattice': {'configuration': TEMPLATE_SUBLATTICE_CONFIGURATION, 'occupancies': TEMPLATE_SUBLATTICE_OCCUPANCIES, 'site_ratios': SUBL_SITE_RATIOS}}

if VERBOSE:
    print("PHASE: {}    CONFIGURATION: {}    OCCUPANCIES: {}    STRUCTURE: {}".format(PHASE_NAME, meta['sublattice']['configuration'], meta['sublattice']['occupancies'], struct.composition.hill_formula))
workflows.append(get_wf_gibbs(struct, deformation_fraction=(-0.05,0.15), phonon=True, phonon_supercell_matrix=SUPERCELL_MATRIX, num_deformations=11, t_max=2000, metadata=meta))

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
