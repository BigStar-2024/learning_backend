from django.db import models
from app.models import RandomSlugModel, TimestampModel, IsActiveModel, ActiveManager
from parler.models import TranslatableModel, TranslatedFields, TranslatableManager
from django.utils.text import slugify


class AchievementManager(ActiveManager, TranslatableManager):
    pass


class Achievement(TimestampModel, RandomSlugModel, IsActiveModel, TranslatableModel):

    translations = TranslatedFields(
        name=models.CharField(max_length=128, unique=True)
    )

    slug = models.SlugField(editable=False)
    image = models.ImageField(null=True, blank=True,
                              help_text='The image of the achivement')
    hex_color = models.CharField(
        null=True, blank=True, max_length=16, help_text='The color of the achivement')
    level_required = models.ForeignKey(
        'experiences.Level', on_delete=models.PROTECT, null=True, blank=True)
    engangement_points = models.IntegerField(null=True)
    coins_earned = models.IntegerField(null=True)

    objects = AchievementManager()

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        return super().save(*args, **kwargs)
