
import inspect
from typing import Type
from fastapi import Form, UploadFile, File
from pydantic import BaseModel


def as_form(cls: Type[BaseModel]):
    defaults = cls.__field_defaults__
    new_parameters = []
    for key, value in cls.__annotations__.items():
        default_value = defaults.get(key)
        if value == UploadFile:
            new_parameters.append(
                inspect.Parameter(
                    key,
                    inspect._POSITIONAL_ONLY,
                    default=File(default_value),
                    annotation=value,
                )
            )
            continue
        if default_value is not None:
            new_parameters.append(
                inspect.Parameter(
                    key,
                    inspect._POSITIONAL_ONLY,
                    default=Form(default_value),
                    annotation=value,
                )
            )
        else:
            new_parameters.append(
                inspect.Parameter(
                    key, inspect._POSITIONAL_ONLY, default=Form(...), annotation=value
                )
            )
    def as_form_func(**data):
        return cls(**data)
    sig = inspect.signature(as_form_func)
    sig = sig.replace(parameters=new_parameters)
    as_form_func.__signature__ = sig
    cls.as_form = as_form_func
    return cls
