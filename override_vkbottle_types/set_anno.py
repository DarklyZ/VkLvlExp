from pydantic.fields import ModelField

def annotation(cls, name, type, class_validators = None, default = None, required = False):
    cls.__fields__[name] = ModelField(
        name = name, type_ = type, class_validators = class_validators,
        model_config = cls.Config, default = default, required = required
    )