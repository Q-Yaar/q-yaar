from abc import ABC, abstractmethod


class PopoBase(ABC):
    """
    To be implemented by all POPOs.
    """

    @classmethod
    @abstractmethod
    def from_json(cls, config: dict) -> "PopoBase":
        """
        Take json, return the class.
        Expected to be used for
            1. Model property can use this to convert from jsonField and return popo
            2. When getting data from API

        params:
            config: json representation of popo

        returns:
            POPO
        """
        raise NotImplementedError()

    @abstractmethod
    def to_json(self) -> dict:
        """
        Returns json represenation of POPO
        Expected to be used for
            1. saving the POPO to the jsonfield
            2. When sending a response to user (in serializer)

        returns:
            JSON representation of the POPO
        """
        raise NotImplementedError()

    @classmethod
    def default(cls, default_value=None):
        """
        Would return None, if the to_json() method is called
        Can be overridden by Caller classes, if they want to send anything else instead of None

        returns:
            Default POPO or actual Popo with default values
        """
        return cls.DefaultPopo(default_value=default_value)

    class DefaultPopo:
        """
        To be used for None type return in a getter
        """

        def __init__(self, default_value=None):
            self.default_value = default_value

        @classmethod
        def from_json(cls, config: dict):
            raise NotImplementedError()

        def to_json(self) -> None:
            return self.default_value
