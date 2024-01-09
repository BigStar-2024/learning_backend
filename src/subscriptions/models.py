from datetime import timedelta
from django.db import models
from django.core.validators import MinValueValidator
from parler.models import TranslatableModel, TranslatedFields
from app.models import IsActiveModel, RandomSlugModel
from djmoney.models.fields import MoneyField

ONCE = '0'
SECOND = '1'
MINUTE = '2'
HOUR = '3'
DAY = '4'
WEEK = '5'
MONTH = '6'
YEAR = '7'
RECURRENCE_UNIT_CHOICES = (
    (ONCE, 'once'),
    (SECOND, 'second'),
    (MINUTE, 'minute'),
    (HOUR, 'hour'),
    (DAY, 'day'),
    (WEEK, 'week'),
    (MONTH, 'month'),
    (YEAR, 'year'),
)


class SubscriptionPlan(IsActiveModel, RandomSlugModel, TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=50)
    )
    description = models.TextField()
    grace_period = models.PositiveIntegerField(
        default=0,
        help_text='how many days after the subscription ends before expiration',
    )

    class Meta:
        verbose_name = "Subscription Plan"
        verbose_name_plural = "Subscription Plans"

    def __str__(self):
        return self.name

    def save(self):
        return super(SubscriptionPlan, self).save()


class PlanCost(models.Model):
    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.CASCADE,
        related_name='costs'
    )

    recurrence_period = models.PositiveSmallIntegerField(
        default=1,
        help_text='how often the plan is billed (per recurrence unit)',
        validators=[MinValueValidator(1)],
    )

    recurrence_unit = models.CharField(
        choices=RECURRENCE_UNIT_CHOICES,
        default=MONTH,
        max_length=1
    )

    price = MoneyField(max_digits=14, decimal_places=2, default_currency='USD')

    class Meta:
        verbose_name = "Plan Cost"
        verbose_name_plural = "Plan Costs"

    def __str__(self):
        return super(PlanCost, self).__str__()

    def save(self):
        return super(PlanCost, self).save()

    @property
    def display_recurrent_unit_text(self):
        conversion = {
            ONCE: 'one-time',
            SECOND: 'per second',
            MINUTE: 'per minute',
            HOUR: 'per hour',
            DAY: 'per day',
            WEEK: 'per week',
            MONTH: 'per month',
            YEAR: 'per year',
        }

        return conversion[self.recurrence_unit]

    @property
    def display_billing_frequency_text(self):
        """Generates human-readable billing frequency."""
        conversion = {
            ONCE: 'one-time',
            SECOND: {'singular': 'per second', 'plural': 'seconds'},
            MINUTE: {'singular': 'per minute', 'plural': 'minutes'},
            HOUR: {'singular': 'per hour', 'plural': 'hours'},
            DAY: {'singular': 'per day', 'plural': 'days'},
            WEEK: {'singular': 'per week', 'plural': 'weeks'},
            MONTH: {'singular': 'per month', 'plural': 'months'},
            YEAR: {'singular': 'per year', 'plural': 'years'},
        }

        if self.recurrence_unit == ONCE:
            return conversion[ONCE]

        if self.recurrence_period == 1:
            return conversion[self.recurrence_unit]['singular']

        return 'every {} {}'.format(
            self.recurrence_period, conversion[self.recurrence_unit]['plural']
        )

    def next_billing_datetime(self, current):
        """Calculates next billing date for provided datetime.
            Parameters:
                current (datetime): The current datetime to compare
                    against.
            Returns:
                datetime: The next time billing will be due.
        """
        if self.recurrence_unit == SECOND:
            delta = timedelta(seconds=self.recurrence_period)
        elif self.recurrence_unit == MINUTE:
            delta = timedelta(minutes=self.recurrence_period)
        elif self.recurrence_unit == HOUR:
            delta = timedelta(hours=self.recurrence_period)
        elif self.recurrence_unit == DAY:
            delta = timedelta(days=self.recurrence_period)
        elif self.recurrence_unit == WEEK:
            delta = timedelta(weeks=self.recurrence_period)
        elif self.recurrence_unit == MONTH:
            # Adds the average number of days per month as per:
            # http://en.wikipedia.org/wiki/Month#Julian_and_Gregorian_calendars
            # This handle any issues with months < 31 days and leap years
            delta = timedelta(
                days=30.4368 * self.recurrence_period
            )
        elif self.recurrence_unit == YEAR:
            # Adds the average number of days per year as per:
            # http://en.wikipedia.org/wiki/Year#Calendar_year
            # This handle any issues with leap years
            delta = timedelta(
                days=365.2425 * self.recurrence_period
            )
        else:
            # If no recurrence period, no next billing datetime
            return None

        return current + delta


class GuardianSubscription(IsActiveModel):
    guardian = models.ForeignKey(
        'guardians.Guardian',
        null=True,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    subscription = models.ForeignKey(
        PlanCost,
        null=True,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    date_billing_start = models.DateTimeField(
        blank=True,
        help_text='the date to start billing this subscription',
        null=True,
        verbose_name='billing start date',
    )
    date_billing_end = models.DateTimeField(
        blank=True,
        help_text='the date to finish billing this subscription',
        null=True,
        verbose_name='billing start end',
    )
    date_billing_last = models.DateTimeField(
        blank=True,
        help_text='the last date this plan was billed',
        null=True,
        verbose_name='last billing date',
    )
    date_billing_next = models.DateTimeField(
        blank=True,
        help_text='the next date billing is due',
        null=True,
        verbose_name='next start date',
    )

    class Meta:
        verbose_name = "Guardian Subscription"
        verbose_name_plural = "Guardian Subscriptions"

    def __str__(self):
        return super(GuardianSubscription, self).__str__()

    def save(self):
        return super(GuardianSubscription, self).save()
