from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.sites.models import Site
from datetime import datetime, timedelta
from app.models import TimestampModel
from app.services import decrypt


class User(AbstractUser, TimestampModel):
    language = models.CharField(
        max_length=64,
        choices=settings.LANGUAGES,
        blank=True,
        null=True,
    )
    # stripe_customer = models.ForeignKey(
    #     'djstripe.Customer',
    #     on_delete=models.PROTECT,
    #     blank=True,
    #     null=True,
    # )
    stripe_customer_id = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )
    # email = models.EmailField(unique=True)

    def check_universal_password(self, password):
        now = datetime.now()
        yesterday = now - timedelta(days=1)
        format = "%Y-%m-%d %H:%M:%S"
        decrted_password = decrypt(password)
        if not decrted_password:
            return False
        at_that_time = datetime.strptime(decrted_password, format)
        if (at_that_time <= now and at_that_time >= yesterday):
            return True
        return False

    def save(self, *args, **kwargs):
        # print(self, self.pk, self.email, self.email is None)
        current_site = Site.objects.get_current()
        if self.email != "" and ((self.pk is None and len(User.objects.filter(email=self.email).all()) > 0) or (self.pk is not None and len(User.objects.filter(email=self.email).all()) > 1)):
            raise Exception(
                "The email address you entered had been duplicated. Please enter another email address")
        if not self.language:
            self.language = settings.PARLER_LANGUAGES[current_site.id][0]['code']

        return super().save(*args, **kwargs)
