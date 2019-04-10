#!/usr/bin/env python
"""
# Gibbs.py
Tool for doing Gibbs energy calculations.

## Running
1. Get the structure you want, e.g. NI.POSCAR
2. Set up files to do a first relaxation `python vib.py relax NI.POSCAR --postfix=-1`
3. Run the files, `cd relax-1 && vasp_std && cd ..`
4. Set up files to do a second relaxation `python vib.py relax relax-1/CONTCAR --postfix=-2`
5. Run the files, `cd relax-2 && vasp_std && cd ..`
6. Set up the phonon calculations `python vib.py phonon relax-2/CONTCAR`
7. Run them `for ff in ls */static */phonon; do cd $ff && vasp_std && cd ../.. ; done`
8. Post process (see phonopy)
# 8a. for ff in ls {00..10}; do echo $ff; done
In each directory, run:
8a. `phonopy --fc vasprun.xml`
8b. create a mesh.conf of
```
ATOM_NAME = Ni
DIM = 1 1 1
MP = 12 12 12
CELL_FILENAME = POSCAR
```
8ca. Create the thermal properties (if LEPSILON used, run `phonopy-vasp-born vasprun.xml`) `phonopy --readfc -tp --nac  mesh.conf` (note LEPSILON can be expensive relative to simple calculations)
8cb. `phonopy --readfc -tp  mesh.conf` (`for ff in {00..10}; do cp mesh.conf $ff/phonon && cd $ff/phonon && phonopy --fc vasprun.xml && phonopy --readfc -tp --tmax=1800 -s mesh.conf && phonopy --readfc -p -s mesh.conf && cd ../.. ; done`)
8d. Create electronic F(T) for all V `phonopy-vasp-efe --tmax=1500 {00..10}/phonon/vasprun.xml`
8e. `phonopy-qha -s --tmax=1300 --efe fe-v.dat e-v.dat {00..10}/phonon/thermal_properties.yaml`

## TODO
- Handle input of magnetic moments
- Make phonopy input files for post-processing (phonon and electron, all inputs)
- Handle status with a couple files .STATUS.READY, .STATUS.RUNNING, .STATUS.COMPLETE, which are used to track progress for automated running
- Run post-processing automatically.
"""


import numpy as np
import copy
import os
from pymatgen import Structure
from dfttk.input_sets import RelaxSet, ForceConstantsSet, StaticSet
import click

def safe_mkdir(dirname):
    try:
        os.mkdir(dirname)
    except FileExistsError:
        pass

def format_int_pad(i, digits):
    return ("{:0"+str(digits)+"d}").format(i)

@click.group()
def cli():
    pass

@click.command()
@click.argument('structure')
@click.option('--postfix', default="", help='Directory postfix, e.g. "-1" gives a directory name of "relax-1" (default="")')
def relax(structure, postfix):
    s = Structure.from_file(structure)
    dirname = "relax"+postfix
    safe_mkdir(dirname)
    relax = RelaxSet(s)
    relax.write_input(dirname)


@click.command()
@click.argument('structure')
@click.option('--nimages', default=11, help='Number of images to use (default=11).')
@click.option('--minfrac', default=0.95, help='Minimum volume scaling factor.')
@click.option('--maxfrac', default=1.10, help='Maximum volume scaling factor.')
def phonon(structure, nimages, minfrac, maxfrac):
    s = Structure.from_file(structure)
    max_dir_digits = len(str(nimages))

    volume_scale_factors = np.linspace(minfrac, maxfrac, nimages).tolist()
    for i, vsf in enumerate(volume_scale_factors):
        # make directory for phonon and static calculations
        dirname = format_int_pad(i, max_dir_digits)
        safe_mkdir(dirname)

        # copy and scale the structure to use, should be relaxed
        new_s = copy.deepcopy(s)
        new_s.scale_lattice(new_s.volume*vsf)

        static = StaticSet(new_s)
        static.write_input(os.path.join(dirname, 'static'))

        phonon = ForceConstantsSet(new_s)
        phonon.write_input(os.path.join(dirname, 'phonon'))


@click.command()
@click.argument('structure')
@click.argument('scaling_matrix')
@click.option('-o', '--output', default='SPOSCAR', help='Make a supercell using 1, 3, or 9 matrix elements')
def supercell(structure, scaling_matrix, output):
    s = Structure.from_file(structure)
    scaling_matrix = [int(i) for i in scaling_matrix.split()]
    if len(scaling_matrix) == 1:
        mat = np.array(scaling_matrix[0])
    elif len(scaling_matrix) == 3:
        mat = np.array(scaling_matrix)
    elif len(scaling_matrix) == 9:
        mat = np.array(scaling_matrix).reshape(3,3)
    else:
        print("Failed to make supercell matrix: found {}".format(mat))
    s.make_supercell(mat)
    s.to(filename=output)

cli.add_command(relax)
cli.add_command(phonon)
cli.add_command(supercell)

if __name__ == '__main__':
    cli()