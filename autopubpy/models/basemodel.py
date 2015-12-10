"""This module contains functions and base classes
for Publisher models.

"""
from abc import ABCMeta, abstractmethod
import json


class BasesJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, JSONable):
            return obj._container
        return super(BasesJSONEncoder, self).default(obj)


json_encoder = BasesJSONEncoder(ensure_ascii = False)


#if not is_JSONable(value):
#    raise ValueError("Value must be jsonable. Cannot JSON {}.".format())
def is_JSONable(obj, encoder=json_encoder):
    """Returns whether or not an object can be converted
    to JSON.
    
    Args:
        encoder: The JSON encoder to test against.

    """
    try:
        encoded_string = json_encoder.encode(obj)
    except Exception as e:
        return False
    return True


class MetaJSON(ABCMeta):
    """An object that works."""

    @abstractmethod
    def as_json(self):
        """Returns the object in it's json form."""


class JSONable(object):
    __metaclass__ = MetaJSON
