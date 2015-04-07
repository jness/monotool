import logging

def get_logger(log_level='INFO'):
    _format = '%(asctime)s - %(levelname)s - %(message)s'
    logging.basicConfig(format=_format)
    logger = logging.getLogger('monotool')  # shouldn't be hard coded.
    logger.setLevel(getattr(logging, log_level))
    return logger