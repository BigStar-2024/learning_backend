from django.db import models
from django.contrib import admin
from ..managers.topics import TopicManager
from django.utils.text import slugify
from mptt.models import MPTTModel, TreeForeignKey
from parler.models import TranslatableModel, TranslatedFields
from app.models import RandomSlugModel, TimestampModel, UUIDModel, IsActiveModel


class Prerequisite(UUIDModel):
    PREFIX = 'prerequisite_'

    topic = models.OneToOneField(
        'Topic',
        on_delete=models.PROTECT,
        related_name="Topic"
    )
    prerequisites = models.ManyToManyField('Topic', blank=True)
    information = models.TextField(null=True, blank=True)

    def __str__(self):
        return f'{self.topic}'

    def get_prerequisites(self):
        return "\n".join([p.name for p in self.prerequisites.all()])


class Topic(
        TimestampModel,
        RandomSlugModel,
        IsActiveModel,
        MPTTModel,
        TranslatableModel):
    PREFIX = 'topic_'

    translations = TranslatedFields(
        name=models.CharField(max_length=256)
    )

    area_of_knowledge = models.ForeignKey(
        'kb.AreaOfKnowledge',
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )
    parent = TreeForeignKey(
        'self',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='sub_topics'
    )
    video_assistor = models.URLField(null=True, blank=True)
    standard_topic = models.CharField(max_length=16, blank=True, null=True)

    objects = TopicManager()

    @property
    def prerequisites(self):
        try:
            prerequisites = Prerequisite.objects.get(
                topic=self).prerequisites.all()
        except Prerequisite.DoesNotExist:
            prerequisites = None
        return prerequisites

    @property
    def prerequisites_str(self):
        prerequisites_str = ""
        prerequisites = self.prerequisites
        if(prerequisites is not None): 
            prerequisites_str = " ".join(str(prerequisite) + "///" for prerequisite in prerequisites)
            prerequisites_str = prerequisites_str[:len(prerequisites_str) - 3]
        # return prerequisites_str
        return prerequisites_str
        
    def mastery_level(self, student):
        from students.models import StudentTopicMastery
        mastery_level = StudentTopicMastery.objects.get(
            student=student, topic=self).mastery_level
        return mastery_level

    def __str__(self):
        return self.safe_translation_getter("name", any_language=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name or '')

        if self.parent:
            self.area_of_knowledge = self.parent.area_of_knowledge
        sup = super().save(*args, **kwargs)
        return sup


class TopicGrade(TimestampModel, UUIDModel, IsActiveModel):
    PREFIX = 'topic_grade_'

    grade = models.ForeignKey(
        'kb.Grade',
        on_delete=models.PROTECT,
    )
    topic = models.ForeignKey(
        'kb.Topic',
        on_delete=models.PROTECT,
    )
    standard_code = models.CharField(max_length=128, null=True, blank=True)

    @admin.display(description='Audience')
    def grade_audience(self):
        return self.grade.audience

    def __str__(self):
        return '{}/{}'.format(self.topic, self.grade)


class GradePrerequisite(UUIDModel):
    PREFIX = 'grade_prerequisite_'

    area_of_knowledge = models.ForeignKey(
        'kb.AreaOfKnowledge',
        on_delete=models.PROTECT,
    )
    grade = models.ForeignKey(
        'kb.Grade',
        on_delete=models.PROTECT,
    )
    mastery = models.ManyToManyField(
        'Topic',
        related_name='mastery_start',
        blank=True,
    )
    competence = models.ManyToManyField(
        'Topic',
        related_name='competence_start',
        blank=True,
    )
