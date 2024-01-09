from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from mptt.managers import TreeManager, TreeQuerySet
from parler.models import TranslatableModel, TranslatedFields, TranslatableManager
from parler.managers import TranslatableQuerySet
from app.models import RandomSlugModel, TimestampModel, IsActiveModel, ActiveManager
from students.models import Student
from treasuretrack.models import WeeklyTreasure
from wallets.models import Withdraw
from django.utils.html import strip_tags


class BadgeManager(ActiveManager, TranslatableManager):
    pass

class Badge(
        TimestampModel,
        RandomSlugModel,
        IsActiveModel,
        TranslatableModel):

    PREFIX = 'badge_'
    GOLD = 'Gold'
    SILVER = 'Silver'
    BRONZE = 'Bronze'
    type_choices = [
        (GOLD, 'Gold'),
        (SILVER, 'Silver'),
        (BRONZE, 'Bronze'),
    ]
    translations = TranslatedFields(
        name=models.CharField(max_length=128, null=True),
    )
    type = models.CharField(max_length=128, choices = type_choices, null=True)
    image = models.URLField(null=True)
    objects = BadgeManager()
    def __str__(self):
        return strip_tags(
        self.safe_translation_getter("name", any_language=True)
    )[:100]


class StudentBadge(
        TimestampModel,
        RandomSlugModel,
        IsActiveModel
    ):

    badge = models.ForeignKey(
        Badge, on_delete=models.PROTECT, null=True)
    student = models.ForeignKey(
        Student, on_delete=models.PROTECT, null=True)
    weekley_treasure = models.OneToOneField(WeeklyTreasure, on_delete=models.CASCADE, null=True, blank=True)
