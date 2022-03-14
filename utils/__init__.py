class Data:
	def __init_subclass__(cls, init = False):
		if init:
			for k, v in cls.__dict__.items():
				if not k.startswith('_'): setattr(Data, k, v)
			cls()