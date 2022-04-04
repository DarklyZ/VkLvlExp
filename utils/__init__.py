from abc import ABC, abstractmethod

class Data:
	def __init_subclass__(cls, write = False):
		if write:
			for k, v in cls.__dict__.items():
				if not k[0] == '_': setattr(Data, k, v)

	@abstractmethod
	def __run__(self):
		pass

	def run(self):
		return self.__run__()