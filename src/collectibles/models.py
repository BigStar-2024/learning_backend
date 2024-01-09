from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from mptt.managers import TreeManager, TreeQuerySet
from parler.models import TranslatableModel, TranslatedFields, TranslatableManager
from parler.managers import TranslatableQuerySet
from app.models import RandomSlugModel, TimestampModel, IsActiveModel, ActiveManager
from wallets.models import Withdraw


class CollectibleCategoryQuerySet(TranslatableQuerySet, TreeQuerySet):
    def as_manager(cls):
        manager = CollectibleCategoryManager.from_queryset(cls)()
        manager._built_with_as_manager = True
        return manager
    as_manager.queryset_only = True
    as_manager = classmethod(as_manager)


class CollectibleCategoryManager(
        ActiveManager,
        TreeManager,
        TranslatableManager):
    _queryset_class = CollectibleCategoryQuerySet


class CollectibleManager(ActiveManager, TranslatableManager):
    pass


class CollectibleCategory(
        TimestampModel,
        MPTTModel,
        RandomSlugModel,
        TranslatableModel,
        IsActiveModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=128, null=True),
        description=models.TextField(null=True)
    )

    parent = TreeForeignKey(
        'self',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='sub_categories'
    )

    front_image = models.URLField(null=True)
    back_image = models.URLField(null=True)
    price = models.IntegerField(default=100)
    firebase_name = models.CharField(max_length=64)

    objects = CollectibleCategoryManager()


class Description(TranslatableModel):
    translations = TranslatedFields(
        key=models.CharField(max_length=32, null=True, blank=True),
        value=models.TextField()
    )


class Collectible(
        TimestampModel,
        RandomSlugModel,
        IsActiveModel,
        TranslatableModel):
    COMMON = 'Common'
    RARE = 'Rare'
    LEGENDARY = 'Legendary'
    EPIC = 'Epic'
    TIER_CHOICES = [
        (COMMON, 'Common'),
        (RARE, 'Rare'),
        (LEGENDARY, 'Legendary'),
        (EPIC, 'Epic'),
    ]

    translations = TranslatedFields(
        name=models.CharField(max_length=128, null=True),
    )
    description = models.ManyToManyField(
        Description,
        through='CollectibleDescription',
        through_fields=('collectible', 'description'),
    )
    image = models.URLField(null=True)
    category = models.ForeignKey(
        'collectibles.CollectibleCategory',
        on_delete=models.PROTECT,
        null=True,
        blank=True)
    objects = CollectibleManager()
    tier = models.CharField(
        choices=TIER_CHOICES,
        max_length=32,
    )


class CollectibleDescription(models.Model):
    collectible = models.ForeignKey(Collectible, on_delete=models.CASCADE)
    description = models.ForeignKey(Description, on_delete=models.PROTECT)


class CollectiblePackPurchaseTransaction(Withdraw):
    collectibles = models.ManyToManyField(Collectible, blank=True)
    collectible_category = models.ForeignKey(
        CollectibleCategory, on_delete=models.PROTECT, null=True)

    def assign_collectibles(self):
        for collectible in self.collectibles.all():
            student_collectible, new = StudentCollectible.objects.get_or_create(
                collectible=collectible, student=self.account.student)
            if new is False:
                student_collectible.amount += 1
            student_collectible.save()


class CollectiblePurchaseTransaction(Withdraw):
    collectible = models.ForeignKey(
        Collectible, on_delete=models.PROTECT, null=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.amount = self.collectible.price
        super().save(*args, **kwargs)
        student_collectible, new = StudentCollectible.objects.get_or_create(
            collectible=self.collectible, student=self.account.student)
        return super().save(*args, **kwargs)


class StudentCollectible(TimestampModel, RandomSlugModel, IsActiveModel):
    collectible = models.ForeignKey(
        'collectibles.Collectible', on_delete=models.PROTECT, null=True)
    student = models.ForeignKey(
        'students.Student', on_delete=models.PROTECT, null=True)
    amount = models.IntegerField(default=1)
