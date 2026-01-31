from dataclasses import dataclass

from common.popo import PopoBase


@dataclass(init=True, repr=False, eq=False)
class RewardConfig(PopoBase):
    # Just a wrapper class, actual classes defined in reward_types_map.py
    pass
