class Data:
	def __init_subclass__(cls, write = False, run = False):
		if write:
			for k, v in cls.__dict__.items():
				if k[0] != '_': setattr(Data, k, v)
		if run:
			cls().__run__()