##############
# User Input #
##############

DRY_RUN = False  # Don't submit the workflows
VERBOSE = True   # Turn on printing of substitutions

# Filename of the template structure to use, usually a dilute or SQS structure
TEMPLATE_STRUCTURE_FILENAME = 'structures/BCC_A2/BCC_A2.Cr2.POSCAR'

# sublattice configuration of the template structure.
# This will be substitued exactly, this does not need to be sorted,
# however the individual configurations to build should be sorted.
TEMPLATE_SUBLATTICE_CONFIGURATION = [['Cr']]
TEMPLATE_SUBLATTICE_OCCUPANCIES = [[1.0]]
SUBL_SITE_RATIOS = [1.0]

# phonon supercell matrix
SUPERCELL_MATRIX = [[4,0,0],[0,4,0],[0,0,4]]

PHASE_NAME = 'BCC_A2'

configurations_to_build = [  # list of sublattice configurations in DFTTK format
[['Cr']],
]

# Dictionary of densities for each pure element.
DENSITY_DICT = {
    'Al': 2.72,    # fcc
    'Co': 8.96,    # hcp
    'Cr': 7.463,   # bcc
    'Cu': 8.888,   # fcc
    'Fe': 8.028,   # bcc
    'Mg': 1.752,   # hcp
    'Mo': 10.025,  # bcc
    'Nb': 8.428,   # bcc
    'Ni': 9.03,    # fcc
    'Ti': 4.58,    # hcp
    'V': 6.313,    # bcc
    'W': 18.854,   # bcc
    'Zn': 6.981,   # hcp
}


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

temp_struct.add_site_property('magmom', [-2.0, 2.0])

for config in configurations_to_build:
    struct, meta = substitute_configuration_with_metadata(temp_struct, TEMPLATE_SUBLATTICE_CONFIGURATION, config, DENSITY_DICT, TEMPLATE_SUBLATTICE_OCCUPANCIES, PHASE_NAME, SUBL_SITE_RATIOS )
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
