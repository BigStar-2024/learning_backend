from django.db import models
from parler.models import TranslatableModel, TranslatedFields, TranslatableManager
from app.models import RandomSlugModel, TimestampModel, IsActiveModel, ActiveManager
from wallets.models import Deposit


class BlockTypeManager(ActiveManager, TranslatableManager):
    pass


class BlockConfiguration(TimestampModel):
    """
    Model for key-value pair configurations for a block.
    These come from the block type configuration and are copied on block creation.
    Examples:
    - Show Timer: True
    """

    # FK's
    block = models.ForeignKey(
        'block.Block',
        on_delete=models.PROTECT,
    )
    key = models.ForeignKey(
        'block.BlockConfigurationKeyword',
        on_delete=models.PROTECT,
    )

    # Attributes
    value = models.CharField(max_length=128, null=True)


class BlockConfigurationKeyword(TimestampModel, IsActiveModel):
    """
    Model for configuration keyword.
    These change the behavior of a block.
    Examples:
    - Show timer
    - Allow to pass on questions
    """

    # Attributes
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name


class BlockType(
    TimestampModel,
    RandomSlugModel,
    IsActiveModel,
    TranslatableModel):
    """
    Model for types of blocks.
    These take some config values and are copied to blocks upon block creation.
    Examples:
    - Assessment
    - Beat The Clock
    """

    PREFIX = 'block_type_'

    # Attributes
    translations = TranslatedFields(
        name=models.CharField(max_length=128)
    )
    objects = BlockTypeManager()


class BlockTypeConfiguration(TimestampModel, IsActiveModel):
    """
    Model for key-value pairs configurations for a block type
    Examples:
    - Show Timer: True
    """

    # FK's
    block_type = models.ForeignKey(
        'block.BlockType',
        on_delete=models.PROTECT,
    )
    key = models.ForeignKey(
        'block.BlockConfigurationKeyword',
        on_delete=models.PROTECT,
    )

    # Attributes
    value = models.CharField(max_length=128)


class Block(TimestampModel, RandomSlugModel, IsActiveModel):
    PREFIX = 'block_'

    BLOCK_SIZE = 10

    MODALITY_AI = 'AI'
    MODALITY_PATH = 'PATH'
    MODALITY_PRACTICE = 'HOMEWORK'
    MODALITY_TEST = 'TEST'

    MODALITY_CHOICES = (
        (MODALITY_AI, 'AI'),
        (MODALITY_PATH, 'Choose your path'),
        (MODALITY_PRACTICE, 'Homework'),
        (MODALITY_TEST, 'Test'),

    )

    # FK's
    type_of = models.ForeignKey(
        'block.BlockType',
        on_delete=models.PROTECT,
        blank=True,
        null=True
    )
    students = models.ManyToManyField(
        'students.Student',
        blank=True
    )
    topic_grade = models.ForeignKey(
        'kb.TopicGrade',
        on_delete=models.PROTECT,
        help_text='This are the topics covered in this block'
    )
    questions = models.ManyToManyField(
        'kb.Question',
        blank=True,
    )

    # Attributes
    modality = models.CharField(
        max_length=128,
        choices=MODALITY_CHOICES,
        default=MODALITY_AI
    )
    block_size = models.IntegerField(default=BLOCK_SIZE)

    # Metrics
    experience_points_available = models.PositiveSmallIntegerField(default=100)
    coins_available = models.PositiveSmallIntegerField(default=100)
    coins_per_question = models.PositiveSmallIntegerField(default=10)

    student_homework = models.ForeignKey(
        'students.StudentHomework',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    def save(self, *args, **kwargs):
        is_new = False
        if not self.pk:
            is_new = True

        if is_new:
            if self.type_of:
                for item in self.type_of.blocktypeconfiguration_set.all():
                    self.blockconfiguration_set.create(
                        key=item.key,
                        value=item.value,
                    )

        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.topic_grade} / {self.modality}"


class BlockPresentation(IsActiveModel, TimestampModel, RandomSlugModel):
    PREFIX = 'block_presentation_'

    # FK's
    block = models.ForeignKey(
        Block,
        on_delete=models.CASCADE,
    )
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
    )

    # Metrics
    hits = models.IntegerField(default=0, null=True)
    errors = models.IntegerField(default=0, null=True)
    total = models.IntegerField(default=0, null=True)
    points = models.IntegerField(null=True)
    bonusCoins = models.IntegerField(default=0, null=True)
    coins = models.IntegerField(default=0, null=True)
    start_timestamp = models.DateTimeField(auto_now_add=True, null=True)
    end_timestamp = models.DateTimeField(null=True)

    def save(self, *args, **kwargs):
        self.total = self.errors + self.hits
        return super().save(*args, **kwargs)


class BlockTransaction(Deposit):
    blockPresentation = models.ForeignKey(
        BlockPresentation, on_delete=models.PROTECT, null=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.amount = self.blockPresentation.coins + self.blockPresentation.bonusCoins
            self.comment = "Answer the questions."
        super().save(*args, **kwargs)
    #     return super().save(*args, **kwargs)


class BlockQuestionPresentation(IsActiveModel, TimestampModel, RandomSlugModel):
    PREFIX = 'block_question_presentation'

    STATUS_PENDING = 'PENDING'
    STATUS_CORRECT = 'CORRECT'
    STATUS_INCORRECT = 'INCORRECT'

    STATUS_CHOICES = (
        (STATUS_PENDING, 'Pending'),
        (STATUS_CORRECT, 'Correct'),
        (STATUS_INCORRECT, 'Incorrect'),
    )

    # FK's
    block_presentation = models.ForeignKey(
        BlockPresentation,
        on_delete=models.CASCADE,
    )
    question = models.ForeignKey(
        'kb.Question',
        on_delete=models.PROTECT
    )
    chosen_answer = models.ManyToManyField(
        'kb.AnswerOption',
    )
    typed_answer = models.CharField(max_length=128, blank=True, null=True)
    topic = models.ForeignKey(
        'kb.Topic',
        on_delete=models.PROTECT,
    )

    # Attributes
    status = models.CharField(
        max_length=32,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING
    )

    @property
    def is_correct(self):
        if self.status == self.STATUS_CORRECT:
            return True
        elif self.status == self.STATUS_INCORRECT:
            return False

    def is_answered(self):
        if self.status != self.STATUS_PENDING:
            return True
        else:
            return False

    def save(self, *args, **kwargs):
        self.topic = self.block_presentation.block.topic_grade.topic
        is_correct = True

        # if self.pk:
        #     if self.typed_answer is None:
        #         for answer in self.chosen_answer.all():
        #             if not answer.is_correct:
        #                 is_correct = False

        #         if is_correct:
        #             self.status = self.STATUS_CORRECT
        #         elif not is_correct:
        #             self.status = self.STATUS_INCORRECT
        #         else:
        #             self.status = self.STATUS_PENDING

        super(BlockQuestionPresentation, self).save(*args, **kwargs)

class StudentBlockQuestionPresentationHistory(TimestampModel):
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, blank=False, null=False)
    block_question_presentation = models.ManyToManyField(BlockQuestionPresentation, blank=False)

class BlockAssignment(TimestampModel):
    PREFIX = 'block_assignment'

    # FK's
    block = models.ForeignKey(
        Block,
        on_delete=models.PROTECT,
        blank=False,
        null=False
    )
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        blank=False,
        null=False
    )

    # Attributes
    order = models.PositiveSmallIntegerField(
        default=0,
        blank=False,
        null=False
    )

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.block} / {self.student}"
