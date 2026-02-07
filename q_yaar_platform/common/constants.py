import enum


class BaseIntEnum(enum.IntEnum):
    @classmethod
    def tokentype_from_string(cls, token_type: str) -> "BaseIntEnum":
        """
        Override if call caps standard names won't work

        throws: KeyError for invalid token_type
        """
        return cls.__members__[token_type]

    @classmethod
    def get_string_for_type(cls, token_type: "BaseIntEnum") -> str:
        """
        Override if call caps standard names won't work

        throws: AttributeError if invalid token_type passed
        """

        return token_type.name

    @classmethod
    def get_choices(cls) -> list[tuple]:
        """
        To be used as choices field in model definition
        """
        return [(member.value, member.name) for member in cls]


class Length:
    USER_NAME = 32
    PHONE_NUMBER = 14
    GAME_CODE = 8
    GAME_NAME = 255
    TEAM_NAME = 100
    TEAM_COLOUR = 50
    CARD_TAG = 100
    CARD_TITLE = 100
    CARD_IMAGE_URL = 200
    REWARD_NAME = 100
    QUESTION_CATEGORY = 100
    PLACEHOLDER_NAME = 100
    PLACEHOLDER_VALUE = 255


class ModuleErrorPrefix:
    JWT_AUTH = "AUTH"
    ACCOUNT = "ACC"
    PROFILE_PLAYER = "PLYR"
    PROFILE_GAME_MASTER = "GMST"
    CARD_DECK = "CRD"
    GAME = "GAM"
    QNA = "QNA"
    FACT = "FACT"


class UserRolesType(BaseIntEnum):
    PLAYER = 1
    GAME_MASTER = 2


class GameType(BaseIntEnum):
    HIDE_N_SEEK = 1


class GameStatus(BaseIntEnum):
    PENDING = 1
    IN_PROGRESS = 2
    COMPLETED = 3


class CardType(BaseIntEnum):
    CURSE = 1
    POWERUP = 2


class CardPile(BaseIntEnum):
    DECK = 1
    HAND = 2
    DISCARD = 3


class QuestionRewardType(BaseIntEnum):
    CARD_DRAW = 1


class QuestionAnswerType(BaseIntEnum):
    IMAGE = 1


class FactType(BaseIntEnum):
    TEXT = 1
    IMAGE = 2
    GEO = 3
