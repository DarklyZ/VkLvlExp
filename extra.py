def isint(arg):
	try: int(arg)
	except: return False
	else: return True

def ispos(arg):
	if arg[0] == '-': return False
	return isint(arg)