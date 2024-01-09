from django.db import models
from django.utils.text import slugify
from mptt.models import MPTTModel, TreeForeignKey
from app.models import RandomSlugModel, TimestampModel, IsActiveModel


class UniversalTopic(TimestampModel, RandomSlugModel, IsActiveModel, MPTTModel):
    PREFIX = 'universal_topic_'

    name = models.CharField(max_length=128)
    slug = models.SlugField(editable=False)
    area_of_knowledge = models.ForeignKey(
        'universals.UniversalAreaOfKnowledge', on_delete=models.PROTECT, null=True, blank=True)
    parent = TreeForeignKey('self', on_delete=models.PROTECT,
                            null=True, blank=True, related_name='sub_topics')
    standard_code = models.CharField(max_length=128, null=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        if self.parent:
            self.area_of_knowledge = self.parent.area_of_knowledge
        sup = super().save(*args, **kwargs)
        return sup
