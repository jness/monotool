from subprocess import Popen, PIPE
from datetime import datetime
import shutil
import tarfile
import os

from config import get_config
from logger import get_logger


def run(command):
    """
    Runs a command and returns a tuple of stdout and stderr
    """
    logger = get_logger(__name__)
    config = get_config()
    logger.info('Running command %s' % command)
    process = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()

    if process.returncode:
        logger.error(stdout)
        raise Exception('Command returned with non zero return')

    logger.debug(stdout)
    logger.info('Command successful')
    return stdout, stderr, process.returncode

def timestamp(verbose=True):
    """
    Returns a human readable timestamp.
    """
    if verbose:
        return datetime.now().strftime("%A, %d. %B %Y %I:%M%p")
    return datetime.now().strftime("%Y%m%d%H%M%S")

def write(filename, data):
    """
    Write to a file.
    """
    logger = get_logger(__name__)
    logger.debug('Writing to %s' % filename)
    f = open(filename, 'w')
    f.write(data)
    f.close()

def read(filename):
    """
    Read from a file.
    """
    f = open(filename, 'r')
    data = f.read()
    f.close()
    return data

def delete(filename):
    """
    Deletes a file or directory.
    """
    logger = get_logger(__name__)
    if os.path.isfile(filename):
        logger.debug('Deleting file %s' % filename)
        os.remove(filename)
    else:
        logger.debug('Deleting directory %s' % filename)
        shutil.rmtree(filename)

def copy(path, dest):
    """
    Copy a file or directory to destination.
    """
    logger = get_logger(__name__)
    logger.debug('Copying %s => %s' % (path, dest))
    try:
        shutil.copyfile(path, dest)
    except IOError:
        shutil.copytree(path, dest)

def mktar(path, dest):
    """
    Creates a tar.gz from path and saves it to dest.
    """
    with tarfile.open(dest, "w:gz") as tar:
        tar.add(path, arcname='')
