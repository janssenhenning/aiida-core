# -*- coding: utf-8 -*-
###########################################################################
# Copyright (c), The AiiDA team. All rights reserved.                     #
# This file is part of the AiiDA code.                                    #
#                                                                         #
# The code is hosted on GitHub at https://github.com/aiidateam/aiida-core #
# For further information on the license, see the LICENSE.txt file        #
# For further information please visit http://www.aiida.net               #
###########################################################################
"""Module to define the database models for the SqlAlchemy backend."""
import sqlalchemy as sa
from sqlalchemy.orm import mapper

# SqlAlchemy does not set default values for table columns upon construction of a new instance, but will only do so
# when storing the instance. Any attributes that do not have a value but have a defined default, will be populated with
# this default. This does mean however, that before the instance is stored, these attributes are undefined, for example
# the UUID of a new instance. In Django this behavior is the opposite and more in intuitive because when one creates for
# example a `Node` instance in memory, it will already have a UUID. The following function call will force SqlAlchemy to
# behave the same as Django and set model attribute defaults upon instantiation. Note that this functionality used to be
# provided by the ``sqlalchemy_utils.force_instant_defaults`` utility function. However, this function's behavior was
# changed in v0.37.5, where the ``sqlalchemy_utils.listeners.instant_defaults_listener`` was changed to update the
# original ``kwargs`` passed to the constructor, with the default values from the column definitions. This broke the
# constructor of certain of our database models, e.g. `DbComment`, which needs to distinguish between the value of the
# ``mtime`` column being defined by the caller as opposed to the default. This is why we revert this change by copying
# the old implementation of the listener.


def instant_defaults_listener(target, _, __):
    """Loop over the columns of the target model instance and populate defaults."""
    for key, column in sa.inspect(target.__class__).columns.items():
        if hasattr(column, 'default') and column.default is not None:
            if callable(column.default.arg):
                setattr(target, key, column.default.arg(target))
            else:
                setattr(target, key, column.default.arg)


sa.event.listen(mapper, 'init', instant_defaults_listener)
