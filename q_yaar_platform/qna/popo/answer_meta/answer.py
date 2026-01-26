from dataclasses import dataclass

from common.popo import PopoBase


@dataclass(init=True, repr=False, eq=False)
class AnswerConfig(PopoBase):
    # Just a wrapper class, actual classes defined in answer_types_map.py
    pass
