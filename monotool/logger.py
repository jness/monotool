import logging
import sys

from app import logfile

def get_logger(name):
	"""
	Logger for logging INFO level to stdout and DEBUG level
	to monotool.log
	"""
	format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
	logger = logging.getLogger(name)
	logger.setLevel(logging.DEBUG)

	# if we have handlers this is an existing logger
	if not logger.handlers:
		ch = logging.StreamHandler(sys.stdout)
		ch.setFormatter(format)
		ch.setLevel(logging.INFO)
		logger.addHandler(ch)

		fh = logging.FileHandler(logfile())
		fh.setFormatter(format)
		fh.setLevel(logging.DEBUG)
		logger.addHandler(fh)

	return logger
