class Data:
	def __init_subclass__(cls, run = False):
		for k, v in cls.__annotations__.items():
			if v is Data: setattr(Data, k, getattr(cls, k))
		if run:
			cls().__run__()