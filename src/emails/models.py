import enum
from pyexpat import model
from django.db import models

from app.models import TimestampModel

# Not use
class SubscriptionType(models.Model):
    name = models.CharField(max_length=64)

# Not use
class Subscription(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.PROTECT)
    subscription_type = models.ManyToManyField(SubscriptionType, blank=True)

class EmailTemplate(TimestampModel):
    PREFIX = 'email_template'
    name = models.CharField('template name', max_length=128, null=False, blank=False, unique=True ) # guardian, teacher, subscriber
    content = models.TextField(null=True)

class EmailHistory(TimestampModel):
    email_template = models.ForeignKey('emails.EmailTemplate', on_delete=models.PROTECT, null=True, blank=True)
    user = models.ForeignKey('users.User', on_delete=models.PROTECT)
    success = models.BooleanField(default=False)
    note = models.CharField('reason note', max_length=256, null=True, blank=True)