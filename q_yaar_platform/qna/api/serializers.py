from common.constants import QuestionRewardType
from qna.models import QuestionCategory, QuestionReward
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


class QuestionCategorySerializer(serializers.ModelSerializer):
    category_id = serializers.SerializerMethodField()
    reward = serializers.SerializerMethodField()

    class Meta:
        model = QuestionCategory
        fields = ("category_id", "category_name", "reward", "priority", "created", "modified")

    def get_category_id(self, obj: QuestionCategory) -> str:
        return str(obj.get_external_id())

    def get_reward(self, obj: QuestionCategory) -> dict:
        return QuestionRewardSerializer(obj.reward).data
