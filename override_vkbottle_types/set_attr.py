from pydantic.fields import ModelField

class SetAttr:
    def __init__(self, cls, name):
        self.cls = cls
        self.name = name

    def __call__(self, type):
        self.set(self.cls, self.name, type)
        return type

    @staticmethod
    def set(cls, name, type, class_validators = None, default = None, required = False):
        cls.__fields__[name] = ModelField(
            name = name, type_ = type, class_validators = class_validators,
            model_config = cls.Config, default = default, required = required
        )
