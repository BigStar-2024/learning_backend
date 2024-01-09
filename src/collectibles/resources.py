from app.resources import TranslatableModelResource
from import_export.fields import Field
from import_export.resources import ModelResource
from .models import Collectible, Description, CollectibleDescription


class CollectibleResource(TranslatableModelResource):
    language_code = Field(
        attribute='_current_language'
    )

    name = Field(
        attribute='name'
    )

    class Meta:
        model = Collectible
        skip_unchanged = True
        report_skipped = False
        fields = (
            'id',
            'language_code',
            'name',
            'category',
            'image',
            'tier',
        )


class DescriptionResource(TranslatableModelResource):
    language_code = Field(
        attribute='_current_language'
    )

    key = Field(
        attribute='key'
    )

    value = Field(
        attribute='value'
    )

    class Meta:
        model = Description
        skip_unchanged = True
        report_skipped = False
        fields = (
            'id',
            'key',
            'value',
        )


class CollectibleDescriptionResource(ModelResource):
    class Meta:
        model = CollectibleDescription
        skip_unchanged = True
        report_skipped = False
        fields = (
            'id',
            'collectible',
            'description',
        )
