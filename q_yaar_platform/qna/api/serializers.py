from common.constants import QuestionRewardType
from qna.models import AskedQuestion, QuestionCategory, QuestionReward, QuestionTemplate
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
    geo = serializers.SerializerMethodField()

    class Meta:
        model = QuestionTemplate
        fields = ("question_id", "template", "category", "geo", "created", "modified")

    def get_question_id(self, obj: QuestionTemplate) -> str:
        return str(obj.get_external_id())

    def get_category(self, obj: QuestionTemplate) -> dict:
        return QuestionCategorySerializer(obj.category).data

    def get_geo(self, obj: QuestionTemplate) -> dict:
        return obj.get_geo().to_json()


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


class AskedQuestionDetailSerializer(serializers.ModelSerializer):
    question_id = serializers.SerializerMethodField()
    question_template_id = serializers.SerializerMethodField()
    rendered_question = serializers.SerializerMethodField()
    template = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    geo = serializers.SerializerMethodField()
    question_meta = serializers.SerializerMethodField()
    answer_meta = serializers.SerializerMethodField()
    reward = serializers.SerializerMethodField()

    class Meta:
        model = AskedQuestion
        fields = (
            "question_id",
            "question_template_id",
            "rendered_question",
            "template",
            "category",
            "geo",
            "question_meta",
            "answer_meta",
            "answered",
            "accepted",
            "reward",
            "created",
            "modified",
        )

    def get_question_id(self, obj: AskedQuestion) -> str:
        return str(obj.get_external_id())

    def get_question_template_id(self, obj: AskedQuestion) -> str:
        return str(obj.game_question.question_template.get_external_id())

    def get_rendered_question(self, obj: AskedQuestion) -> str:
        return obj.render()

    def get_template(self, obj: AskedQuestion) -> str:
        return obj.game_question.question_template.template

    def get_category(self, obj: AskedQuestion) -> dict:
        return QuestionCategorySerializer(obj.game_question.question_template.category).data

    def get_geo(self, obj: AskedQuestion) -> dict:
        return obj.game_question.question_template.get_geo_count().to_json()

    def get_question_meta(self, obj: AskedQuestion) -> dict:
        return obj.get_question_meta().to_json()

    def get_answer_meta(self, obj: AskedQuestion) -> dict:
        return obj.get_answer_meta().to_json()

    def get_reward(self, obj: AskedQuestion) -> dict:
        return QuestionRewardSerializer(obj.game_question.question_template.category.reward).data
