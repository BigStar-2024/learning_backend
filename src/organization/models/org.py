from django.db import models
from django.utils.text import slugify
from mptt.models import MPTTModel, TreeForeignKey
from app.models import RandomSlugModel, TimestampModel, IsActiveModel


class Organization(MPTTModel, TimestampModel, RandomSlugModel, IsActiveModel):
    PREFIX = 'org_'

    name = models.CharField(max_length=128, null=True)
    type_of = models.CharField(max_length=128, null=True)
    slug = models.SlugField(editable=False)
    parent = TreeForeignKey('self', on_delete=models.PROTECT,
                            null=True, blank=True, related_name='sub_organizations')
    student_plan = models.ManyToManyField('plans.StudentPlan', blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        return super().save(*args, **kwargs)


class OrganizationPersonnel(TimestampModel, RandomSlugModel, IsActiveModel):
    GENDER_MALE = 'MALE'
    GENDER_FEMALE = 'FEMALE'
    GENDER_OTHER = 'OTHER'
    GENDER_CHOICES = (
        (GENDER_MALE, 'Male'),
        (GENDER_FEMALE, 'Female'),
        (GENDER_OTHER, 'Other'),
    )

    PREFIX = 'org_personnel_'

    user = models.OneToOneField(
        'users.User',
        on_delete=models.PROTECT,
        null=True
    )
    organization = models.ForeignKey(
        'organization.Organization',
        on_delete=models.PROTECT,
        null=True
    )

    name = models.CharField(max_length=128, null=True)
    last_name = models.CharField(max_length=128, null=True)
    gender = models.CharField(max_length=8, null=True, choices=GENDER_CHOICES)
    date_of_birth = models.DateField(null=True)
    identification_number = models.CharField(max_length=128, null=True)
    position = models.CharField(max_length=128, null=True)

    def __str__(self):
        return self.name+' '+self.last_name
