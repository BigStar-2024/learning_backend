import os
from django.db import models
from django.contrib import admin
from ckeditor.fields import RichTextField
from polymorphic.models import PolymorphicModel
from kb.managers.content import (
    QuestionManager, AnswerOptionManager
)
from gtts import gTTS
from django.utils.html import strip_tags
from django.conf import settings
from pathlib import Path

from parler.models import TranslatableModel, TranslatedFields
from app.models import RandomSlugModel, TimestampModel, IsActiveModel
from time import sleep
from bs4 import BeautifulSoup
import pathlib


class Question(
        TimestampModel,
        RandomSlugModel,
        IsActiveModel,
        TranslatableModel):

    class QuestionType(models.TextChoices):
        MULTIPLE_CHOICE = 'MC', 'Multiple Choice'
        MULTIPLE_SELECT = 'MS', 'Multiple Select'
        ORDER = 'O', 'Order'
        RELATE = 'R', 'Relate'
        TYPE_IN = 'T', 'Type In'

    PREFIX = 'question_'
    translations = TranslatedFields(
        question_text=RichTextField(blank=True)
    )
    topic = models.ForeignKey(
        'kb.Topic', on_delete=models.PROTECT)
    grade = models.ForeignKey(
        'kb.Grade', on_delete=models.PROTECT)
    objects = QuestionManager()
    question_type = models.CharField(
        max_length=2,
        choices=QuestionType.choices,
    )

    def __str__(self):
        return strip_tags(
            self.safe_translation_getter(
                "question_text",
                any_language=True
            )
        )[:100]

    def __repr__(self):
        return strip_tags(
            self.safe_translation_getter(
                "question_text",
                any_language=True
            )
        )[:100]

    def get_questionimageasset_set(self):
        return QuestionImageAsset.objects.filter(question=self)

    def get_questionvideoasset_set(self):
        return QuestionVideoAsset.objects.filter(question=self)

    def get_questionaudioasset_set(self):
        return QuestionAudioAsset.objects.filter(question=self)

    def get_questionttsasset(self, language):
        return QuestionTTSAsset.objects.get(question=self, language=language)

    def save_gtts(self):

        language = self.get_available_languages()[0]

        question_text = self.safe_translation_getter(
            "question_text", language_code=language)

        if not question_text:
            return None

        new = False
        try:
            question_tts_asset, new = QuestionTTSAsset.objects.get_or_create(
                question=self,
                language=language
            )
        except Exception as e:
            print("After", e)
            return

        try:
            tts_file = question_tts_asset.tts_file.file
        except Exception as e:
            tts_file = None
            print(e)

        if new or (tts_file is None) or (tts_file and os.stat(str(tts_file)).st_size == 0):
            question_path = os.path.join(
                settings.MEDIA_ROOT, f'tts/{language}/{self.identifier}/')

            Path(question_path).mkdir(parents=True, exist_ok=True)

            tts_file_name = f'{self.identifier}.mp3'

            tts_file_path = os.path.join(question_path, tts_file_name)
            with open(tts_file_path, 'wb') as f:
                try:
                    # print(question_text)
                    tts = gTTS(text=BeautifulSoup(question_text, 'lxml').text, lang=(
                        "es-us" if language == "es-mx" else language))
                    tts.write_to_fp(f)
                    question_tts_asset.tts_file = f'tts/{language}/{self.identifier}/{self.identifier}.mp3'
                    question_tts_asset.save()
                    sleep(50)
                except Exception as e:
                    print("Exception on gtts", e)
        else:
            print("tts_file is existing")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    @ admin.display(description='Question')
    def question(self):
        return self.safe_translation_getter("question_text", any_language=True)

    @ admin.display(description='Audience')
    def grade_audience(self):
        return self.grade.audience

    @ admin.display(description='Topic identifier')
    def topic_identifier(self):
        return self.topic.identifier


class QuestionAsset(TimestampModel, RandomSlugModel, PolymorphicModel):

    class Meta:
        ordering = ['order']

    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(blank=True, null=True)

    @ admin.display(description='Question identifier')
    def question_slug(self):
        return self.question.random_slug

    def save(self, *args, **kwargs):
        if self.order is None:
            self.order = QuestionAsset.objects.filter(
                question=self.question).count() + 1
        return super().save(*args, **kwargs)


class QuestionImageAsset(QuestionAsset):
    PREFIX = 'question_image_asset_'
    image = models.URLField()


class QuestionAudioAsset(QuestionAsset):
    PREFIX = 'question_audio_asset_'
    # audio_file = models.FileField()
    audio_file = models.URLField(null=True)


class QuestionTTSAsset(QuestionAsset):
    PREFIX = 'question_tts_asset_'
    tts_file = models.FileField(null=True, blank=True, upload_to='tts')
    language = models.CharField(max_length=256, null=True, blank=True)

    def save(self, *args, **kwargs):
        try:
            return super().save(*args, **kwargs)
        except Exception as e:
            print("Super creation is failed", e)


class QuestionVideoAsset(QuestionAsset):
    PREFIX = 'question_video_asset_'
    url = models.URLField()


class AnswerOption(
    TimestampModel,
    RandomSlugModel,
    TranslatableModel,
    PolymorphicModel
):
    PREFIX = 'answer_option_'
    question = models.ForeignKey(Question, on_delete=models.PROTECT)
    is_correct = models.BooleanField(default=False)

    objects = AnswerOptionManager()

    def get_answeroptionttsasset(self, language):
        return AnswerTTSAsset.objects.get(answer_option=self, language=language)

    @admin.display(description='Question type')
    def question_type(self):
        return self.question.question_type

    @admin.display(description='Answer')
    def answer_display(self):
        return self.__str__

    @property
    def tts_audio_url(self):
        if (not self.get_available_languages):
            return None
        language = self.get_available_languages()[0]
        return self.get_answeroptionttsasset(language)

    def save_gtts(self):
        if (not self.answer_text):
            return None

        language = self.get_available_languages()[0]

        answer_text = self.safe_translation_getter(
            "answer_text", language_code=language)

        if not answer_text:
            return None

        answer_option = self.answeroption_ptr
        answer_tts_asset, new = AnswerTTSAsset.objects.get_or_create(
            answer_option=self,
            language=language
        )
        try:
            tts_file = self.tts_file.file
        except Exception as e:
            tts_file = None
            print(e)
        if new or (tts_file is None):
            question_path = os.path.join(
                settings.MEDIA_ROOT, f'tts/{language}/{self.question.identifier}/')

            Path(question_path).mkdir(parents=True, exist_ok=True)

            tts_file_name = f'{self.identifier}.mp3'

            tts_file_path = os.path.join(question_path, tts_file_name)

            with open(tts_file_path, 'wb') as f:
                try:
                    tts = gTTS(text=BeautifulSoup(answer_text, 'lxml').text, lang=(
                        "es-us" if language == "es-mx" else language))
                    sleep(30)
                    tts.write_to_fp(f)
                    answer_tts_asset.tts_file = f'tts/{language}/{self.question.identifier}/{self.identifier}.mp3'
                    answer_tts_asset.save()
                    print("file url is", answer_tts_asset.tts_file)
                except Exception as e:
                    print("Exception on gtts", e)
            # time.sleep(10)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class AnswerAsset(TimestampModel, RandomSlugModel, PolymorphicModel):

    class Meta:
        ordering = ['order']

    answer_option = models.ForeignKey(AnswerOption, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(blank=True, null=True)

    @ admin.display(description='Question identifier')
    def answer_option_slug(self):
        return self.answer_option.random_slug

    def save(self, *args, **kwargs):
        if self.order is None:
            self.order = AnswerAsset.objects.filter(
                answer_option=self.answer_option).count() + 1
        return super().save(*args, **kwargs)


class AnswerTTSAsset(AnswerAsset):
    PREFIX = 'answer_tts_asset_'
    tts_file = models.FileField(null=True, blank=True, upload_to='tts')
    language = models.CharField(max_length=256, null=True, blank=True)


class MultipleChoiceAnswerOption(AnswerOption):
    translations = TranslatedFields(
        answer_text=models.CharField(max_length=256),
        explanation=RichTextField(null=True, blank=True),
        image=models.URLField(null=True, blank=True),
        audio_file=models.URLField(null=True, blank=True),
        video=models.URLField(null=True, blank=True),
    )

    def __str__(self):
        return strip_tags(self.safe_translation_getter("answer_text", any_language=True))


class MultipleSelectAnswerOption(AnswerOption):
    translations = TranslatedFields(
        answer_text=models.CharField(max_length=256),
        explanation=RichTextField(null=True, blank=True),
        image=models.URLField(null=True, blank=True),
        audio_file=models.URLField(null=True, blank=True),
        video=models.URLField(null=True, blank=True),
    )

    def __str__(self):
        return strip_tags(self.safe_translation_getter("answer_text", any_language=True))


class TypeInAnswerOption(AnswerOption):
    translations = TranslatedFields(
        answer_text=models.CharField(max_length=256),
        explanation=RichTextField(null=True, blank=True),
        image=models.URLField(null=True, blank=True),
        audio_file=models.URLField(null=True, blank=True),
        video=models.URLField(null=True, blank=True),
    )
    case_sensitive = models.BooleanField(default=False)

    def __str__(self):
        return strip_tags(self.safe_translation_getter("answer_text", any_language=True))


class OrderAnswerOption(AnswerOption):
    translations = TranslatedFields(
        answer_text=models.CharField(max_length=256),
        image=models.URLField(null=True, blank=True),
        audio_file=models.URLField(null=True, blank=True),
        video=models.URLField(null=True, blank=True),
    )
    order = models.IntegerField()

    def __str__(self):
        return strip_tags(self.safe_translation_getter("answer_text", any_language=True))


class RelateAnswerOption(AnswerOption):
    translations = TranslatedFields(
        key=models.CharField(max_length=256),
        value=models.CharField(max_length=256),
        key_image=models.URLField(null=True, blank=True),
        value_image=models.URLField(null=True, blank=True),
    )

    def __str__(self):
        return strip_tags(
            self.safe_translation_getter("key", any_language=True)
            + " - "
            + self.safe_translation_getter("value", any_language=True)
        )
