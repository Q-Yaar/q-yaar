from common.constants import QuestionRewardType
from qna.models import QuestionCategory, QuestionReward, QuestionTemplate
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


class QuestionSerializer(serializers.ModelSerializer):
    question_id = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()

    class Meta:
        model = QuestionTemplate
        fields = ("question_id", "template", "category", "created", "modified")

    def get_question_id(self, obj: QuestionTemplate) -> str:
        return str(obj.get_external_id())

    def get_category(self, obj: QuestionTemplate) -> dict:
        return QuestionCategorySerializer(obj.category).data


class QuestionDetailSerializer(QuestionSerializer):
    placeholders = serializers.SerializerMethodField()

    class Meta:
        model = QuestionTemplate
        fields = QuestionSerializer.Meta.fields + ("placeholders",)

    def get_placeholders(self, obj: QuestionTemplate) -> dict:
        placeholders_data = {}
        for placeholder in obj.placeholders.all():
            placeholders_data[placeholder.placeholder_name] = {
                "required": placeholder.required,
                "allowed_values": [allowed_value.value for allowed_value in placeholder.allowed_values.all()],
            }
        return placeholders_data
