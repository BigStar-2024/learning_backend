from django.db import models
from app.models import RandomSlugModel, TimestampModel, IsActiveModel, ActiveManager
from parler.models import TranslatableModel, TranslatedFields, TranslatableManager
from django.utils.text import slugify


class AudienceManager(ActiveManager, TranslatableManager):
    pass


class Audience(TimestampModel, RandomSlugModel, IsActiveModel, TranslatableModel):
    PREFIX = 'audience_'

    translations = TranslatedFields(
        name=models.CharField(max_length=128, unique=True)
    )
    slug = models.SlugField(editable=False, unique=True)

    standard_code = models.CharField(max_length=4, null=True)

    objects = AudienceManager()

    def __str__(self):
        return self.safe_translation_getter("name", any_language=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        return super().save(*args, **kwargs)
