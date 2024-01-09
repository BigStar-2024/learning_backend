from django.db import models
from app.models import IsActiveModel, TimestampModel
from wallets.models import Deposit


class WeeklyTreasureLevel(IsActiveModel):
    name = models.CharField(max_length=128)
    level = models.PositiveIntegerField(
        unique=True,
    )
    coins_required = models.PositiveIntegerField()
    correct_questions_required = models.PositiveIntegerField()
    bonus_coins = models.PositiveIntegerField()
    bonus_badge = models.ForeignKey(
        'badges.Badge', blank=True, on_delete=models.PROTECT, null=True)
    bonus_collectible = models.ManyToManyField(
        'collectibles.Collectible', blank=True)

    class Meta:
        ordering = ['level']

    def get_previous_level(self):
        return WeeklyTreasureLevel.objects.get(level=self.level-1)

    def __str__(self):
        return self.name


class WeeklyTreasure(IsActiveModel):
    level = models.ForeignKey(WeeklyTreasureLevel, on_delete=models.PROTECT)
    coins_awarded = models.PositiveIntegerField(blank=True, null=True)
    collectibles_awarded = models.ManyToManyField(
        'collectibles.Collectible', blank=True)
    badge_awarded = models.ForeignKey('badges.Badge', on_delete=models.PROTECT, null=True)


class StudentWeeklyTreasure(TimestampModel):
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE)
    weekly_treasure = models.ForeignKey(WeeklyTreasure, on_delete=models.CASCADE)


class WeeklyTreasureTransaction(Deposit):
    student_weekly_treasure = models.ForeignKey(
        StudentWeeklyTreasure,
        on_delete=models.CASCADE
    )

    def save(self, *args, **kwargs):
        if not self.pk:
            self.amount = self.student_weekly_treasure.weekly_treasure.coins_awarded
            self.comment = "Daiy Treasure Coins"
            # if not self.coins_awarded:
            #     self.amount = 0
            # if self.collectibles_awarded:
            #     for collectible in self.collectibles_awarded.all():
            #         student_collectible, new = StudentCollectible.objects.get_or_create(
            #             student=self.account.user.student,
            #             collectible=collectible,
            #         )
            #         if not new:
            #             student_collectible.amount += 1
            #         student_collectible.save()
            #     self.comment = "Daiy Treasure Collectible"
            # if self.coins_awarded and self.collectibles_awarded:
            #     self.comment = "Daiy Treasure Coins & Collectible"
        super().save(*args, **kwargs)
