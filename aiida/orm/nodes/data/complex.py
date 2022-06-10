# -*- coding: utf-8 -*-
###########################################################################
# Copyright (c), The AiiDA team. All rights reserved.                     #
# This file is part of the AiiDA code.                                    #
#                                                                         #
# The code is hosted on GitHub at https://github.com/aiidateam/aiida-core #
# For further information on the license, see the LICENSE.txt file        #
# For further information please visit http://www.aiida.net               #
###########################################################################
"""`Data` sub class to represent a complex float value."""

import numbers

from .base import to_aiida_type
from .numeric import NumericType

__all__ = ('Complex',)


class Complex(NumericType):
    """`Data` sub class to represent a float value."""

    _type = complex


@to_aiida_type.register(numbers.Complex)
def _(value):
    return Complex(value)
