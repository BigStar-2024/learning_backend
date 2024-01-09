from django.db import models
from app.models import RandomSlugModel, TimestampModel, IsActiveModel
from django.utils.text import slugify


class UniversalAreaOfKnowledge(TimestampModel, RandomSlugModel, IsActiveModel):
    PREFIX = 'universal_aok_'

    name = models.CharField(max_length=128, unique=True)
    slug = models.SlugField(editable=False)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        return super().save(*args, **kwargs)
