from common.constants import QuestionRewardType
from qna.models import QuestionReward
from rest_framework import serializers


class QuestionRewardSerializer(serializers.ModelSerializer):
    reward_id = serializers.SerializerMethodField()
    reward_type = serializers.SerializerMethodField()
    reward_meta = serializers.SerializerMethodField()

    class Meta:
        model = QuestionReward
        fields = ("reward_id", "reward_name", "reward_type", "reward_meta", "created", "modified")

    def get_reward_id(self, obj: QuestionReward) -> str:
        return str(obj.get_external_id())

    def get_reward_type(self, obj: QuestionReward) -> str:
        return QuestionRewardType.get_string_for_type(QuestionRewardType(obj.reward_type))

    def get_reward_meta(self, obj: QuestionReward) -> dict:
        return obj.get_reward_meta().to_json()
