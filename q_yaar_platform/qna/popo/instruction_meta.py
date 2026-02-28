from dataclasses import dataclass

from common.popo import PopoBase
from qna.popo.question_meta.question import LocationPointListConfig


@dataclass(init=True, repr=False, eq=False)
class AnswerInstructionMeta(PopoBase):
    points: LocationPointListConfig
    radius: str
    hider_location: str  # inside/outside
    split_direction: str  # north/south/east/west
    preferred_point: str  # p1/p2
    area_op_type: str  # inside/outside
    uploaded_area: str
    text: str
    closer_further: str  # closer/further
    selected_line_index: int
    polygon_geo_json: dict
    feature_name: str

    @classmethod
    def from_json(cls, config: dict) -> "AnswerInstructionMeta":
        if not config:
            return cls(
                points=LocationPointListConfig.default(),
                radius=None,
                hider_location=None,
                split_direction=None,
                preferred_point=None,
                area_op_type=None,
                uploaded_area=None,
                text=None,
                closer_further=None,
                selected_line_index=None,
                polygon_geo_json=None,
                feature_name=None,
            )
        return cls(
            points=LocationPointListConfig.from_json(config["points"]),
            radius=config["radius"],
            hider_location=config["hider_location"],
            split_direction=config["split_direction"],
            preferred_point=config["preferred_point"],
            area_op_type=config["area_op_type"],
            uploaded_area=config["uploaded_area"],
            text=config["text"],
            closer_further=config["closer_further"],
            selected_line_index=config["selected_line_index"],
            polygon_geo_json=config["polygon_geo_json"],
            feature_name=config["feature_name"],
        )

    def to_json(self) -> dict:
        return {
            "points": self.points.to_json(),
            "radius": self.radius,
            "hider_location": self.hider_location,
            "split_direction": self.split_direction,
            "preferred_point": self.preferred_point,
            "area_op_type": self.area_op_type,
            "uploaded_area": self.uploaded_area,
            "text": self.text,
            "closer_further": self.closer_further,
            "selected_line_index": self.selected_line_index,
            "polygon_geo_json": self.polygon_geo_json,
            "feature_name": self.feature_name,
        }
