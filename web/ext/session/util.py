





class ParallelLock(object):
    """Parallel read, sequential write lock with a bias towards writers.
    
    Supports several back-ends including in-process threading and on-disk lockfile.
    """
    
    def __new__(cls):
        """Return a bare ParallelLock implementation or one of its subclasses."""
        return ParallelLock.__new__(cls)


class ThreadLocking(object):
    """A back-end for the ParallelLock class which utilizes threading features.

    As such, this back-end is not usable in a multi-process environemnt unless extreme care is taken.
    """
    pass


class FileLocking(object):
    """A back-end for the ParallelLock class which utilizes lockfiles.

    On Unix systems 'link' is atomic, and on Windows 'mkdir' is.  Exploit this.
    """
    pass
