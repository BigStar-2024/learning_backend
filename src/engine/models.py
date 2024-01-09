from django.db import models
from decimal import Decimal
from app.models import TimestampModel


class TopicMasterySettings(models.Model):
    topic = models.ForeignKey(
        'kb.Topic',
        on_delete=models.CASCADE,
        related_name='values'
    )
    sample_size = models.IntegerField(default=20)
    mastery_percentage = models.IntegerField(default=90)
    competence_percentage = models.IntegerField(default=60)


class TopicStudentReport(TimestampModel):
    topic = models.ForeignKey('kb.Topic', on_delete=models.PROTECT)
    student = models.ForeignKey('students.Student', on_delete=models.PROTECT)
    questions_answered = models.IntegerField(default=0)
    correct_question = models.IntegerField(default=0)
    accuracy = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        default=Decimal(0.0)
    )

    def save(self, *args, **kwargs):
        if self.questions_answered > 0:
            self.accuracy = round(self.correct_question /
                                  self.questions_answered * 100, 1)
        super(TopicStudentReport, self).save(*args, **kwargs)


class AreaOfKnowledgeStudentReport(TimestampModel):
    area_of_knowledge = models.ForeignKey(
        'kb.AreaOfKnowledge',
        on_delete=models.PROTECT
    )
    student = models.ForeignKey('students.Student', on_delete=models.PROTECT)
    questions_answered = models.IntegerField(default=0)
    correct_question = models.IntegerField(default=0)
    accuracy = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        default=Decimal(0.0)
    )

    def save(self, *args, **kwargs):
        if self.questions_answered > 0:
            self.accuracy = round(self.correct_question /
                                  self.questions_answered * 100, 1)
        super(AreaOfKnowledgeStudentReport, self).save(*args, **kwargs)
