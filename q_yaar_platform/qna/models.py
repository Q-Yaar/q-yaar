from common.abstract_models import AbstractExternalFacing, AbstractTimeStamped, AbstractVersioned
from common.constants import Length, QuestionRewardType
from django.db import models
from game.models import Game
from qna.popo.reward_meta.reward import RewardConfig
from qna.popo.reward_meta.reward_types_map import REWARD_TYPE_MAP


class QuestionReward(AbstractExternalFacing, AbstractTimeStamped, AbstractVersioned):
    CONST_KEY_REWARD_META = "reward_meta"

    reward_name = models.CharField(max_length=Length.REWARD_NAME, unique=True)
    reward_type = models.PositiveIntegerField(choices=QuestionRewardType.get_choices())

    info = models.JSONField(default=dict, blank=True)

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
    template = models.TextField(help_text="Example: 'Are you within {{ distance }} metres of me?'")
    category = models.ForeignKey(QuestionCategory, on_delete=models.CASCADE, related_name="question_templates")

    def __str__(self):
        return f"{self.external_id}"

    @classmethod
    def create(cls, template: str, category: QuestionCategory) -> "QuestionTemplate":
        question_template = cls(template=template, category=category)
        question_template.save()
        return question_template


class Placeholder(AbstractVersioned):
    question = models.ForeignKey(QuestionTemplate, on_delete=models.CASCADE, related_name="placeholders")
    placeholder_name = models.CharField(max_length=Length.PLACEHOLDER_NAME)
    required = models.BooleanField(default=True)

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
