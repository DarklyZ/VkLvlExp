class Data:
	def __init_subclass__(cls, init = False):
		if init:
			for k, v in cls.__dict__.items():
				if not k[0] == '_': setattr(Data, k, v)
			cls()