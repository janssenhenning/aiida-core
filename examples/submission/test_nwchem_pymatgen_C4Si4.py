#!/usr/bin/env runaiida
# -*- coding: utf-8 -*-

__copyright__ = u"Copyright (c), 2015, ECOLE POLYTECHNIQUE FEDERALE DE LAUSANNE (Theory and Simulation of Materials (THEOS) and National Centre for Computational Design and Discovery of Novel Materials (NCCR MARVEL)), Switzerland and ROBERT BOSCH LLC, USA. All rights reserved."
__license__ = "MIT license, see LICENSE.txt file"
__version__ = "0.5.0"
__contributors__ = "Andrea Cepellotti, Giovanni Pizzi, Nicolas Mounet, Riccardo Sabatini, Valentin Bersier, Andrius Merkys"

import sys
import os

from ase import Atoms

from aiida.common.example_helpers import test_and_get_code
from aiida.common.exceptions import NotExistent

################################################################

ParameterData = DataFactory('parameter')
StructureData = DataFactory('structure')
try:
    dontsend = sys.argv[1]
    if dontsend == "--dont-send":
        submit_test = True
    elif dontsend == "--send":
        submit_test = False
    else:
        raise IndexError
except IndexError:
    print >> sys.stderr, ("The first parameter can only be either "
                          "--send or --dont-send")
    sys.exit(1)

try:
    codename = sys.argv[2]
except IndexError:
    codename = None

queue = None
#queue = "Q_aries_free"
settings = None
#####

code = test_and_get_code(codename, expected_code_type='nwchem.nwcpymatgen')

calc = code.new_calc()
calc.label = "Test NWChem"
calc.description = "Test calculation with the NWChem SCF code"
calc.set_max_wallclock_seconds(30*60) # 30 min
calc.set_resources({"num_machines": 1})

if queue is not None:
    calc.set_queue_name(queue)

parameters = ParameterData(dict={
    'directives': [
        ['set nwpw:minimizer', '2'],
        ['set nwpw:psi_nolattice', '.true.'],
        ['set includestress', '.true.']
    ],
    'geometry_options': [
        'units',
        'au',
        'center',
        'noautosym',
        'noautoz',
        'print'
    ],
    'memory_options': [],
    'symmetry_options': [],
    'tasks': [
        {
            'alternate_directives': {
                'driver': {'clear': '', 'maxiter': 40},
                'nwpw': {'ewald_ncut': 8, 'simulation_cell': '\n  ngrid 16 16 16\n end'}
            },
            'basis_set': {},
            'charge': 0,
            'operation': 'optimize',
            'spin_multiplicity': None,
            'theory': 'pspw',
            'theory_directives': {},
            'title': None
        }
    ],
    'add_cell': True
})

a = Atoms(['Si', 'Si', 'Si' ,'Si', 'C', 'C', 'C', 'C'],
          cell=[8.277, 8.277, 8.277])
a.set_scaled_positions([
    (-0.5, -0.5, -0.5),
    (0.0, 0.0, -0.5),
    (0.0, -0.5, 0.0),
    (-0.5, 0.0, 0.0),
    (-0.25, -0.25, -0.25),
    (0.25 ,0.25 ,-0.25),
    (0.25, -0.25, 0.25),
    (-0.25 ,0.25 ,0.25),
])
struct = StructureData(ase=a)

calc.use_structure(struct)
calc.use_parameters(parameters)

if submit_test:
    subfolder, script_filename = calc.submit_test()
    print "Test_submit for calculation (uuid='{}')".format(
        calc.uuid)
    print "Submit file in {}".format(os.path.join(
        os.path.relpath(subfolder.abspath),
        script_filename
        ))
else:
    calc.store_all()
    print "created calculation; calc=Calculation(uuid='{}') # ID={}".format(
        calc.uuid,calc.dbnode.pk)
    calc.submit()
    print "submitted calculation; calc=Calculation(uuid='{}') # ID={}".format(
        calc.uuid,calc.dbnode.pk)
