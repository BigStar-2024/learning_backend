import uuid
from django.db import models
from django.utils import timezone
from parler.models import TranslatableManager


class ActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)

    def inactive_objects(self):
        return super().get_queryset().filter(is_active=False)


class ActiveManagerTranslated(ActiveManager, TranslatableManager):
    pass


class BaseModel(models.Model):

    PREFIX = ''
    identifier = models.CharField(editable=False, unique=True, max_length=128)

    def get_identifier(self):
        return'{prefix}{id:04}'.format(prefix=self.PREFIX, id=self.pk)

    def save(self, *args, **kwargs):
        self.identifier = self.get_identifier()
        sup = super().save(*args, **kwargs)
        return sup

    def __str__(self):
        valid_str_names = ('name',)
        for valid_str in valid_str_names:
            if getattr(self, valid_str, None):
                return getattr(self, valid_str)
        return super().__str__()

    def get_meta(self):
        return self._meta

    class Meta:
        abstract = True


class IsActiveModel(models.Model):
    is_active = models.BooleanField(default=True)
    objects = ActiveManager()
    all_objects = models.Manager()

    deleted_timestamp = models.DateTimeField(
        'Deleted timestamp', null=True, editable=False)

    def delete(self, *args, **kwargs):
        self.is_active = False
        self.deleted_timestamp = timezone.now()
        self.save(*args, **kwargs)

    def hard_delete(self, *args, **kwargs):
        return super().delete()

    def __str__(self, *args, **kwargs):
        if not self.is_active:
            return super().__str__() + '(SOFT_DELETE)'
        else:
            return super().__str__()

    class Meta:
        abstract = True


class RandomSlugModel(BaseModel):

    SLUG_LENGTH = 10
    random_slug = models.SlugField(editable=False, unique=True)

    def get_identifier(self):
        return '{prefix}{slug}'.format(prefix=self.PREFIX, slug=self.random_slug)

    def save(self, *args, **kwargs):
        if not self.random_slug:
            while True:
                random_slug = uuid.uuid4().hex[:self.SLUG_LENGTH].upper()
                others = self._meta.model.objects.filter(
                    random_slug=random_slug)
                if others.count() == 0:
                    self.random_slug = random_slug
                    break
        sup = super().save(*args, **kwargs)
        return sup

    class Meta:
        abstract = True


class UUIDModel(BaseModel):

    random_slug = models.UUIDField(editable=False, unique=True)

    def get_identifier(self):
        return '{prefix}{slug}'.format(prefix=self.PREFIX, slug=self.random_slug)

    def save(self, *args, **kwargs):
        if not self.random_slug:
            while True:
                random_slug = uuid.uuid4()
                others = self._meta.model.objects.filter(
                    random_slug=random_slug)
                if others.count() == 0:
                    self.random_slug = random_slug
                    break
        sup = super().save(*args, **kwargs)
        return sup

    class Meta:
        abstract = True


class TimestampModel(models.Model):

    create_timestamp = models.DateTimeField(
        'Created timestamp', auto_now_add=True, editable=False, null=True)
    update_timestamp = models.DateTimeField(
        'Updated timestamp', auto_now=True, editable=False, null=True)

    class Meta:
        abstract = True
