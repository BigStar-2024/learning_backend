from .models import Avatar
from import_export.resources import ModelResource

class AvatarResource(ModelResource):
    class Meta:
        model = Avatar
        skip_unchanged = True
        report_skipped = False
        fields = (
            'id',
            'name',
            'type_of',
            'image',
            'price',
        )
