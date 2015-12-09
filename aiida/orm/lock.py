# -*- coding: utf-8 -*-

import aiida.common
from aiida.common.exceptions import (InternalError, ModificationNotAllowed, LockPresent)
from aiida.djsite.db.models import DbLock
from django.utils import timezone

__copyright__ = u"Copyright (c), 2015, ECOLE POLYTECHNIQUE FEDERALE DE LAUSANNE (Theory and Simulation of Materials (THEOS) and National Centre for Computational Design and Discovery of Novel Materials (NCCR MARVEL)), Switzerland and ROBERT BOSCH LLC, USA. All rights reserved."
__license__ = "MIT license, see LICENSE.txt file"
__version__ = "0.5.0"
__contributors__ = "Andrea Cepellotti, Giovanni Pizzi, Nicolas Mounet, Riccardo Sabatini"


class LockManager(object):
    """
    Management class to generate in a db-safe way locks.

    The class handles the generation of lock through the creation of database
    records with unique ``key`` fields using transaction-safe methods.
    """

    def aquire(self, key, timeout=3600, owner="None"):

        """
        The class tries to generate a new DbLock object with a key, unique in the model. If
        the creation goes good the Lock is generated and returned, if not an error is raised.
        :param key: the unique lock key, a string
        :param timeout: how long the 
        :return: a Lock object
        :raise: InternalError: if there is an expired lock with the same input key
        :raise: LockPresent: if there is a Lock already present with the same key 
        """

        from django.db import IntegrityError, transaction

        import time

        try:

            sid = transaction.savepoint()
            dblock = DbLock.objects.create(key=key, timeout=timeout, owner=owner)
            transaction.savepoint_commit(sid)
            return Lock(dblock)

        except IntegrityError:

            transaction.savepoint_rollback(sid)

            old_lock = DbLock.objects.get(key=key)
            timeout_secs = time.mktime(old_lock.creation.timetuple()) + old_lock.timeout
            now_secs = time.mktime(timezone.now().timetuple())

            if now_secs > timeout_secs:
                raise InternalError(
                    "A lock went over the limit timeout, this could mine the integrity of the system. Reload the Daemon to fix the problem.")
            else:
                raise LockPresent("A lock is present.")

        except:
            raise InternalError("Something went wrong, try to keep on.")

    def clear_all(self):

        """
        Clears all the Locks, no matter if expired or not, useful for the bootstrap
        """

        from django.db import IntegrityError, transaction

        try:

            sid = transaction.savepoint()
            DbLock.objects.all().delete()
        except IntegrityError:
            transaction.savepoint_rollback(sid)


class Lock(object):
    """
    ORM class to handle the DbLock objects.

    Handles the release of the Lock, offers utility functions to test if a Lock
    is expired or still valid and to get the lock key.
    """

    def __init__(self, dblock):

        """
        Initialize the Lock object with a DbLock.
        :param dblock: a DbLock object generated by the LockManager
        """

        self.dblock = dblock

    def release(self, owner="None"):

        """
        Releases the lock deleting the DbLock from the database.
        :param owner: a string with the Lock's owner name
        :raise: ModificationNotAllowed: if the input owner is not the lock owner
        :raise: InternalError: if something goes bad with the database 
        """

        if self.dblock == None:
            raise InternalError("No dblock present.")

        try:
            if (self.dblock.owner == owner):
                self.dblock.delete()
                self.dblock = None
            else:
                raise ModificationNotAllowed("Only the owner can release the lock.")

        except:
            raise InternalError("Cannot release a lock, Reload the Daemon to fix the problem.")

    @property
    def isexpired(self):

        """
        Test whether a lock is expired or still valid
        """

        import time

        if self.dblock == None:
            return False

        timeout_secs = time.mktime(self.dblock.creation.timetuple()) + self.dblock.timeout
        now_secs = time.mktime(timezone.now().timetuple())

        if now_secs > timeout_secs:
            return True
        else:
            return False

    @property
    def key(self):

        """
        Get the DbLock key
        :return: string with the lock key
        """

        if self.dblock == None:
            return None

        return self.dblock.key