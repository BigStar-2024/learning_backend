from app.resources import TranslatableModelResource
from import_export.fields import Field
from .models import Game, GameCategory


class GameResource(TranslatableModelResource):
    language_code = Field(
        attribute='_current_language'
    )

    name = Field(
        attribute='name'
    )

    class Meta:
        model = Game
        skip_unchanged = True
        report_skipped = False
        fields = (
            'id',
            'language_code',
            'name',
            'image',
            'cost',
            'play_stats',
            'category'
            'is_active',
        )


class GameCategoryResource(TranslatableModelResource):
    language_code = Field(
        attribute='_current_language'
    )

    name = Field(
        attribute='name'
    )

    class Meta:
        model = GameCategory
        skip_unchanged = True
        report_skipped = False
        fields = (
            'id',
            'language_code',
            'name',
            'image',
            'bg_color'
            'is_active',
        )