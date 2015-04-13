
def app_name():
	"""
	Determine the app_name using __name__'s first index.
	"""
	return __name__.split('.')[0]

def logfile():
	"""
	Returns the application logfile path
	"""
	return '/tmp/%s.log' % app_name()
