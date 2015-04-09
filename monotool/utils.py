from subprocess import Popen, PIPE
from logger import get_logger

def run(command, logger=get_logger('NOTSET')):
    """
    Runs a command and returns a tuple of stdout and stderr
    """
    logger.info('Running command %s' % command)
    process = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    logger.debug(stdout)

    if process.returncode:
        logger.error(stdout)
        if stderr and not self.debug:
            logger.error(stderr)
        raise Exception('Command returned with non zero return')
    logger.info('Command successful')
    return stdout, stderr, process.returncode
