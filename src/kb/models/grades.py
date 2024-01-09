from django.db import models
from django.utils.text import slugify
from parler.models import TranslatableModel, TranslatedFields, TranslatableManager
from app.models import RandomSlugModel, TimestampModel, IsActiveModel, ActiveManager


class GradeManager(ActiveManager, TranslatableManager):
    pass


class Grade(TimestampModel, RandomSlugModel, IsActiveModel, TranslatableModel):
    PREFIX = 'grade_'

    translations = TranslatedFields(
        name=models.CharField(max_length=128, null=True)
    )

    slug = models.SlugField(editable=False)
    audience = models.ForeignKey(
        'audiences.Audience', on_delete=models.PROTECT)

    objects = GradeManager()

    def __str__(self):
        return f'{self.name} / {self.audience}'

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        return super().save(*args, **kwargs)
