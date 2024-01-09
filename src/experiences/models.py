from django.db import models
from parler.models import TranslatableModel, TranslatedFields, TranslatableManager
from app.models import RandomSlugModel, TimestampModel, IsActiveModel, ActiveManager


class LevelManager(ActiveManager, TranslatableManager):
    pass


class Level(TimestampModel, RandomSlugModel, IsActiveModel, TranslatableModel):
    PREFIX = 'level_'

    translations = TranslatedFields(
        name=models.CharField(max_length=128, null=True)
    )

    points_required = models.IntegerField(null=True)
    amount = models.IntegerField(null=False)

    objects = LevelManager()

    def get_next_level(self):
        print("get next level")
        next_level, new = self.__class__.objects.get_or_create(amount = self.amount + 1)
        if(new) :
            for language in self.get_available_languages():
                self.set_current_language(language)
                next_level.set_current_language(language)
                next_level.name = self.name
            next_level.points_required = 100 * (pow(next_level.amount, 1.3))
            next_level.save()
        return next_level


class Battery(TimestampModel):
    student = models.OneToOneField(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='battery',
    )
    level = models.IntegerField(default=0)
