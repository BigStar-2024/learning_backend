from app.resources import TranslatableModelResource
from import_export.fields import Field
from .models import Audience


class AudienceResource(TranslatableModelResource):
    language_code = Field(
        attribute='_current_language'
    )

    name = Field(
        attribute='name'
    )

    class Meta:
        model = Audience
        skip_unchanged = True
        report_skipped = False
        fields = (
            'id',
            'language_code',
            'name',
            'standard_code',
            'is_active',
        )
