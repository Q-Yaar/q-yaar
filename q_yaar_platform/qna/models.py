from common.abstract_models import AbstractExternalFacing, AbstractTimeStamped, AbstractVersioned
from common.constants import AnswerInstructionType, Length, QuestionRewardType
from common.models import FilteredModelManager
from django.db import models
from django.template import Context, Template
from game.models import Game, Team
from qna.popo.answer_meta.answer import AnswerConfig
from qna.popo.instruction_meta import AnswerInstructionMeta
from qna.popo.question_meta.question import QuestionMetaConfig
from qna.popo.question_meta_type.geo_count import GeoCountConfig
from qna.popo.reward_meta.reward import RewardConfig
from qna.popo.reward_meta.reward_types_map import REWARD_TYPE_MAP


class QuestionReward(AbstractExternalFacing, AbstractTimeStamped, AbstractVersioned):
    CONST_KEY_REWARD_META = "reward_meta"

    reward_name = models.CharField(max_length=Length.REWARD_NAME, unique=True)
    reward_type = models.PositiveIntegerField(choices=QuestionRewardType.get_choices())

    info = models.JSONField(default=dict, blank=True)

    objects = FilteredModelManager()

    def __str__(self):
        return self.reward_name

    def get_reward_meta(self) -> RewardConfig:
        return REWARD_TYPE_MAP[self.reward_type].from_json(self.info.get(self.CONST_KEY_REWARD_META, {}))

    def set_reward_meta(self, reward_meta: RewardConfig, save: bool = False) -> "QuestionReward":
        info = self.info
        info[self.CONST_KEY_REWARD_META] = reward_meta.to_json()
        self.info = info
        if save:
            self.save()
        return self

    @classmethod
    def create(cls, reward_name: str, reward_type: QuestionRewardType, reward_meta: RewardConfig) -> "QuestionReward":
        reward = cls(reward_name=reward_name, reward_type=reward_type)
        reward.set_reward_meta(reward_meta)
        reward.save()
        return reward


class QuestionCategory(AbstractExternalFacing, AbstractTimeStamped, AbstractVersioned):
    category_name = models.CharField(max_length=Length.QUESTION_CATEGORY, unique=True)
    reward = models.ForeignKey(QuestionReward, on_delete=models.PROTECT, related_name="question_categories")
    priority = models.PositiveIntegerField()

    objects = FilteredModelManager()

    class Meta:
        indexes = [models.Index(fields=["category_name"])]

    def __str__(self):
        return self.category_name

    @classmethod
    def create(cls, category_name: str, reward: QuestionReward, priority: int) -> "QuestionCategory":
        category = cls(category_name=category_name, reward=reward, priority=priority)
        category.save()
        return category


class QuestionTemplate(AbstractExternalFacing, AbstractTimeStamped, AbstractVersioned):
    GEO_COUNT = "geo"

    template = models.TextField(help_text="Example: 'Are you within {{ distance }} metres of me?'")
    category = models.ForeignKey(QuestionCategory, on_delete=models.CASCADE, related_name="question_templates")
    answer_instruction_type = models.PositiveIntegerField(
        choices=AnswerInstructionType.get_choices(), default=AnswerInstructionType.NO_INSTRUCTION
    )

    info = models.JSONField(default=dict, blank=True)

    objects = FilteredModelManager()

    def __str__(self):
        return f"{self.external_id}"

    def get_geo(self) -> GeoCountConfig:
        return GeoCountConfig.from_json(self.info.get(self.GEO_COUNT, {}))

    def set_geo(self, geo_count: GeoCountConfig, save: bool = False) -> "QuestionTemplate":
        info = self.info
        info[self.GEO_COUNT] = geo_count.to_json()
        self.info = info
        if save:
            self.save()
        return self

    @classmethod
    def create(
        cls,
        template: str,
        category: QuestionCategory,
        answer_instruction_type: AnswerInstructionType,
        geo_count: GeoCountConfig,
    ) -> "QuestionTemplate":
        question_template = cls(template=template, category=category, answer_instruction_type=answer_instruction_type)
        question_template.set_geo(geo_count)
        question_template.save()
        return question_template


class Placeholder(AbstractVersioned):
    question = models.ForeignKey(QuestionTemplate, on_delete=models.CASCADE, related_name="placeholders")
    placeholder_name = models.CharField(max_length=Length.PLACEHOLDER_NAME)
    required = models.BooleanField(default=True)

    objects = FilteredModelManager()

    def __str__(self):
        return f"{self.question.external_id}:{self.placeholder_name}"

    @classmethod
    def create(cls, question: QuestionTemplate, placeholder_name: str, required: bool = True) -> "Placeholder":
        placeholder = cls(question=question, placeholder_name=placeholder_name, required=required)
        placeholder.save()
        return placeholder


class PlaceholderAllowedValue(AbstractVersioned):
    placeholder = models.ForeignKey(Placeholder, on_delete=models.CASCADE, related_name="allowed_values")
    value = models.CharField(max_length=Length.PLACEHOLDER_VALUE)

    objects = FilteredModelManager()

    def __str__(self):
        return f"{self.placeholder.placeholder_name} = {self.value}"

    @classmethod
    def create(cls, placeholder: Placeholder, value: str) -> "PlaceholderAllowedValue":
        allowed_value = cls(placeholder=placeholder, value=value)
        allowed_value.save()
        return allowed_value


class GameQuestion(AbstractTimeStamped):
    question_template = models.ForeignKey(QuestionTemplate, on_delete=models.CASCADE, related_name="game_questions")
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="questions")

    class Meta:
        indexes = [models.Index(fields=["game"])]
        unique_together = (("question_template", "game"),)

    @classmethod
    def create(cls, question_template: QuestionTemplate, game: Game) -> "GameQuestion":
        game_question = cls(question_template=question_template, game=game)
        game_question.save()
        return game_question


class AskedQuestion(AbstractExternalFacing, AbstractTimeStamped):
    # TODO: Add POPOs in future, currently fully flexible.
    CONST_KEY_CHOSEN_PLACEHOLDERS = "chosen_placeholders"

    CONST_KEY_QUESTION_META = "question_meta"
    CONST_KEY_ANSWER_META = "answer_meta"

    CONST_KEY_FACT_META = "fact_meta"

    game_question = models.ForeignKey(GameQuestion, on_delete=models.CASCADE, related_name="asked_questions")
    target = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="asked_questions")

    answered = models.BooleanField(default=False)
    accepted = models.BooleanField(default=False)

    info = models.JSONField(default=dict, blank=True)

    def get_chosen_placeholders(self) -> dict[str, str]:
        return self.info.get(self.CONST_KEY_CHOSEN_PLACEHOLDERS, {})

    def set_chosen_placeholders(self, chosen_placeholders: dict[str, str], save: bool = False) -> "AskedQuestion":
        info = self.info
        info[self.CONST_KEY_CHOSEN_PLACEHOLDERS] = chosen_placeholders
        self.info = info
        if save:
            self.save()
        return self

    def get_question_meta(self) -> QuestionMetaConfig:
        return QuestionMetaConfig.from_json(self.info.get(self.CONST_KEY_QUESTION_META, {}))

    def set_question_meta(self, question_meta: QuestionMetaConfig, save: bool = False) -> "AskedQuestion":
        info = self.info
        info[self.CONST_KEY_QUESTION_META] = question_meta.to_json()
        self.info = info
        if save:
            self.save()
        return self

    def get_answer_meta(self) -> AnswerConfig:
        return AnswerConfig.from_json(self.info.get(self.CONST_KEY_ANSWER_META, {}))

    def set_answer_meta(self, answer_meta: AnswerConfig, save: bool = False) -> "AskedQuestion":
        info = self.info
        info[self.CONST_KEY_ANSWER_META] = answer_meta.to_json()
        self.info = info
        if save:
            self.save()
        return self

    def get_fact_meta(self) -> AnswerInstructionMeta:
        return AnswerInstructionMeta.from_json(self.info.get(self.CONST_KEY_FACT_META, {}))

    def set_fact_meta(self, fact_meta: AnswerInstructionMeta, save: bool = False) -> "AskedQuestion":
        info = self.info
        info[self.CONST_KEY_FACT_META] = fact_meta.to_json()
        self.info = info
        if save:
            self.save()
        return self

    def render(self) -> str:
        return Template(self.game_question.question_template.template).render(Context(self.get_chosen_placeholders()))

    def _validate_placeholders(self, chosen_placeholders: dict[str, str]) -> None:
        for placeholder in self.game_question.question_template.placeholders.all():
            name = placeholder.placeholder_name
            if placeholder.required and name not in chosen_placeholders:
                raise ValueError(f"Missing required placeholder: {name}")
            if name in chosen_placeholders:
                value = chosen_placeholders[name]
                if (
                    placeholder.allowed_values.all().exists()
                    and not placeholder.allowed_values.filter(value=value).exists()
                ):
                    raise ValueError(f"Invalid value for placeholder: {name}")

    @classmethod
    def create(
        cls,
        game_question: GameQuestion,
        target: Team,
        chosen_placeholders: dict[str, str],
        question_meta: QuestionMetaConfig,
    ) -> "AskedQuestion":
        asked_question = cls(game_question=game_question, target=target)
        asked_question._validate_placeholders(chosen_placeholders)
        asked_question.set_chosen_placeholders(chosen_placeholders)
        asked_question.set_question_meta(question_meta)
        asked_question.save()
        return asked_question
