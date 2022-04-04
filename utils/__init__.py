class Data:
	def __init_subclass__(cls, write = False):
		if write:
			for k, v in cls.__dict__.items():
				if k[0] != '_': setattr(Data, k, v)
			cls().__run__()