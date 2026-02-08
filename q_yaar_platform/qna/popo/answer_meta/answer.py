from dataclasses import dataclass

from common.popo import PopoBase


@dataclass(init=True, repr=False, eq=False)
class AnswerConfig(PopoBase):
    result: bool
    metadata: dict

    @classmethod
    def from_json(cls, config: dict) -> "AnswerConfig":
        if not config:
            return cls.default()
        return cls(result=config["result"], metadata=config["metadata"])

    def to_json(self) -> dict:
        return {"result": self.result, "metadata": self.metadata}
