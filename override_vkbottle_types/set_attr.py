from pydantic.fields import ModelField

class SetAttr:
    def __init__(self, cls, name):
        self.cls = cls
        self.name = name

    def __call__(self, type):
        self.set(type)
        return type

    def set(self, type, class_validators = None, default = None, required = False):
        self.cls.__fields__[self.name] = ModelField(
            name = self.name, type_ = type, class_validators = class_validators,
            model_config = self.cls.Config, default = default, required = required
        )
