#!/usr/bin/python3

import os
import errno

from os import (O_RDONLY, O_WRONLY, O_RDWR)

def set_fd0(fd0):
    fd = os.open(fd0[0], fd0[1])
    os.dup2(fd, 0)
    os.close(fd)

def mode2str(mode):
    if mode & 3 == O_RDONLY:
        return 'O_RDONLY'
    elif mode & 3 == O_RDWR:
        return 'O_RDWR'
    elif mode & 3 == O_WRONLY:
        return 'O_WRONLY'
    else:
        return '%d' % (mode & 3)

def errno2str(e):
    if e == 0:
        return 'success'
    else:
        return errno.errorcode[e]

def test(fd0, op, expected_result):
    desc = ('0 = open(%r, %s), %s(%s)' %
            (fd0[0], mode2str(fd0[1]), op[0].__doc__,
             ', '.join(repr(a) for a in op[1:])))

    set_fd0(fd0)
    result = op[0](*op[1:])
    if result == expected_result:
        print('SUCCESS   %s: %s' % (desc, errno2str(result)))
    else:
        print('FAILURE   %s: %s; expected %s' %
              (desc, errno2str(result), errno2str(expected_result)))

def op_open(fn, mode):
    """open"""
    try:
        fd = os.open(fn, mode)
    except OSError as e:
        return e.errno
    else:
        os.close(fd)
        return 0

# Traversal in the middle of the top-level path
test(('.', O_RDONLY), (op_open, '/proc/self/fd/0/null', O_RDONLY), 0)
test(('.', O_RDONLY), (op_open, '/proc/self/fd/0/null', O_RDWR), 0)

# Traversal in a symlink at the end of the top-level path
test(('.', O_RDONLY), (op_open, 'fd0null', O_RDONLY), 0)
test(('.', O_RDONLY), (op_open, 'fd0null', O_RDWR), 0)

# Open directly
test(('null', O_RDONLY), (op_open, '/proc/self/fd/0', O_RDONLY), 0)
test(('null', O_RDONLY), (op_open, '/proc/self/fd/0', O_RDWR), errno.EACCES)
test(('null', O_RDONLY), (op_open, '/proc/self/fd/0', O_WRONLY), errno.EACCES)

# Open via symlink
test(('null', O_RDONLY), (op_open, 'fd0', O_RDONLY), 0)
test(('null', O_RDONLY), (op_open, 'fd0', O_RDWR), errno.EACCES)
test(('null', O_RDONLY), (op_open, 'fd0', O_WRONLY), errno.EACCES)
