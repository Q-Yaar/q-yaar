from dataclasses import dataclass

from common.popo import PopoBase


@dataclass(init=True, repr=False, eq=False)
class FactMetaConfig(PopoBase):
    op_type: str
    op_meta: dict

    @classmethod
    def from_json(cls, config: dict) -> "FactMetaConfig":
        if not config:
            return cls.default()
        return cls(op_type=config["op_type"], op_meta=config["op_meta"])

    def to_json(self) -> dict:
        return {"op_type": self.op_type, "op_meta": self.op_meta}
