from django.db import models
from app.models import (
    RandomSlugModel,
    TimestampModel,
    IsActiveModel,
    ActiveManager
)
from wallets.models import Withdraw
from parler.models import (
    TranslatableModel,
    TranslatedFields,
    TranslatableManager
)
from django.conf import settings
from django.utils.html import strip_tags

import os
import lxml.html as LH


class GameCategoryManager(ActiveManager, TranslatableManager):
    pass


class GameManager(ActiveManager, TranslatableManager):
    pass


class Game(TimestampModel, TranslatableModel, RandomSlugModel, IsActiveModel):
    PREFIX = 'game_'

    translations = TranslatedFields(
        name=models.CharField(max_length=128, null=True)
    )
    image = models.URLField(null=True)
    path = models.CharField(null=False, max_length=30)
    cost = models.IntegerField(
        blank=True,
        null=True
    )
    play_stats = models.BigIntegerField(default=0, null=True)
    category = models.ManyToManyField('games.GameCategory')
    objects = GameManager()

    def __str__(self):
        return strip_tags(
            self.safe_translation_getter("name", any_language=True)
        )[:100]

    def get_game_content(self):
        path = settings.MEDIA_ROOT
        + "games/"
        + self.path
        + "/"
        + self.random_slug
        + "_index.html"
        if not os.path.exists(path):
            initial_path = settings.MEDIA_ROOT + "games/" + self.path + "/"
            if os.path.exists(initial_path + "index.html"):
                initial_path = initial_path + "index.html"
            elif os.path.exists(initial_path + "index.htm"):
                initial_path = initial_path + "index.htm"
            else:
                raise Exception("Game content not exists")
                return
            os.rename(initial_path, path)

        file = open(path, 'r')
        contents = file.read()

        contents_LH = LH.fromstring(contents)
        for element in contents_LH.iter('link'):
            try:
                element.attrib['href'] = (
                    'https://api.withsocrates.com/media/games/'
                    + self.path
                    + "/"
                    + element.attrib['href']
                )
            except Exception as e:
                print(str(e))
        for element in contents_LH.iter(['script', 'img']):
            try:
                element.attrib['src'] = (
                    'https://api.withsocrates.com/media/games/'
                    + self.path
                    + "/"
                    + element.attrib['src']
                )
            except Exception as e:
                print(str(e))

        return LH.tostring(contents_LH, pretty_print=True).decode("utf-8")


class GameCategory(
        TimestampModel,
        TranslatableModel,
        RandomSlugModel,
        IsActiveModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=25, null=True)
    )
    image = models.URLField(null=True)
    bg_color = models.CharField(null=True, blank=True, max_length=16)
    objects = GameCategoryManager()

    def __str__(self):
        return strip_tags(
            self.safe_translation_getter(
                "name",
                any_language=True
            )
        )[:100]


class PlayGameTransaction(Withdraw):
    game = models.ForeignKey(
        Game, on_delete=models.PROTECT, null=True)

    def save(self, price=100, *args, **kwargs):
        if not self.pk:
            # price = kwargs.get('price')
            self.amount = self.game.cost * price / 100
        return super().save(*args, **kwargs)

