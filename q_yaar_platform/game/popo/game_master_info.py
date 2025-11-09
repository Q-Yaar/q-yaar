from dataclasses import dataclass

from common.popo import PopoBase


@dataclass(init=True, repr=False, eq=False)
class GameMasterInfoConfig(PopoBase):
    profile_name: str
    email_id: str
    phone: str

    @classmethod
    def from_json(cls, config: dict) -> "GameMasterInfoConfig":
        return cls(
            profile_name=config.get("profile_name", ""),
            email_id=config.get("email_id", ""),
            phone=config.get("phone", ""),
        )

    def to_json(self) -> dict:
        return {"profile_name": self.profile_name, "email_id": self.email_id, "phone": self.phone}
