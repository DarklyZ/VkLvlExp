from pydantic.fields import ModelField

class Annotation:
    def __init__(self, cls):
        self.cls = cls

    def __getattr__(self, name):
        self.name = name
        return self.annotation

    def annotation(self, type, class_validators = None, default = None, required = False):
        self.cls.__fields__[self.name] = ModelField(
            name = self.name, type_ = type, class_validators = class_validators,
            model_config = self.cls.Config, default = default, required = required
        )