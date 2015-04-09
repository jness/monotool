
def app_name():
	"""
	Determine the app_name using __name__'s first index.
	"""
	return __name__.split('.')[0]
