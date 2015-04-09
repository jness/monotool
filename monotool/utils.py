from subprocess import Popen, PIPE

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
