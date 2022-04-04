from abc import ABC, abstractmethod

class Data:
	def __init_subclass__(cls, write = False):
		if write:
			for k, v in cls.__dict__.items():
				if k == '__run__': setattr(cls, 'run', v)
				elif k[0] != '_': setattr(Data, k, v)