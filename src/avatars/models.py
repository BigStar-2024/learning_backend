from django.db import models
from app.models import RandomSlugModel, TimestampModel, UUIDModel, IsActiveModel
from wallets.models import Withdraw


TYPE_ACCESSORIES = 'ACCESSORIES'
TYPE_HEAD = 'HEAD'
TYPE_CLOTHES = 'CLOTHES'
TYPE_PANTS = 'PANTS'


class Avatar(TimestampModel, UUIDModel, IsActiveModel):
    TYPE_CHOICES = (
        (TYPE_ACCESSORIES, 'Accessories'),
        (TYPE_HEAD, 'Head/Hair'),
        (TYPE_CLOTHES, 'Clothes'),
        (TYPE_PANTS, 'Pants'),
    )

    PREFIX = 'avatar_'

    type_of = models.CharField(max_length=25, null=True, choices=TYPE_CHOICES)
    name = models.CharField(max_length=64, null=True, blank=True)
    image = models.URLField(null=True)
    price = models.DecimalField(
        blank=True, null=True, decimal_places=2, max_digits=15)


class StudentAvatar(TimestampModel, RandomSlugModel, IsActiveModel):
    avatar = models.ForeignKey(
        'avatars.Avatar', on_delete=models.PROTECT, null=True)
    student = models.ForeignKey(
        'students.Student', on_delete=models.PROTECT, null=True)
    in_use = models.BooleanField(default=False)


class FavoriteAvatarCollection(TimestampModel):
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE
    )
    avatar_accessorie = models.ForeignKey(
        'avatars.Avatar',
        on_delete=models.PROTECT,
        limit_choices_to={'type_of': TYPE_ACCESSORIES},
        related_name='+',
        blank=True,
        null=True
    )
    avatar_head = models.ForeignKey(
        'avatars.Avatar',
        on_delete=models.PROTECT,
        limit_choices_to={'type_of': TYPE_HEAD},
        related_name='+',
    )
    avatar_clothes = models.ForeignKey(
        'avatars.Avatar',
        on_delete=models.PROTECT,
        limit_choices_to={'type_of': TYPE_CLOTHES},
        related_name='+',
    )
    avatar_pants = models.ForeignKey(
        'avatars.Avatar',
        on_delete=models.PROTECT,
        limit_choices_to={'type_of': TYPE_PANTS},
        related_name='+',
    )
    skin_tone = models.CharField(
        max_length=7,
        blank=True,
        null=True,
    )

    def set_in_use(self):
        student_avatar = StudentAvatar.objects.filter(student=self.student).filter(
            avatar__in=[
                self.avatar_accessorie.id,
                self.avatar_head.id,
                self.avatar_clothes.id,
                self.avatar_pants.id,
            ]
        ).update(in_use=True)


class AvatarPurchaseTransaction(Withdraw):
    avatar = models.ForeignKey(
        Avatar, on_delete=models.PROTECT, null=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.amount = self.avatar.price
        super().save(*args, **kwargs)
        student_avatar, new = StudentAvatar.objects.get_or_create(
            avatar=self.avatar, student=self.account.student)
        return super().save(*args, **kwargs)
