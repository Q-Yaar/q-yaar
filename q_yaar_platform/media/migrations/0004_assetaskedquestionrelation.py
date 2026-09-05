import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("game", "0008_team_unique_spectator_team_per_game"),
        ("media", "0003_asset_uploaded_by_cascade"),
        ("qna", "0009_remove_placeholderallowedvalue_placeholder_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="AssetAskedQuestionRelation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("modified", models.DateTimeField(auto_now=True)),
                (
                    "asset",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="asked_question_links",
                        to="media.asset",
                    ),
                ),
                (
                    "asked_question",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="asset_links",
                        to="qna.askedquestion",
                    ),
                ),
            ],
            options={
                "indexes": [models.Index(fields=["asked_question"], name="media_assetasked_q_idx")],
                "unique_together": {("asset",)},
            },
        ),
        migrations.RemoveIndex(
            model_name="asset",
            name="media_asset_asked_q_e03445_idx",
        ),
        migrations.RemoveField(
            model_name="asset",
            name="asked_question",
        ),
    ]
