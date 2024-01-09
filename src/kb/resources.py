from app.resources import TranslatableModelResource
from app.widgets import TranslatableForeignKeyWidget
from import_export.fields import Field
from import_export.widgets import ForeignKeyWidget
from import_export.resources import ModelResource
from .models import Topic, Grade, TopicGrade, Prerequisite, GradePrerequisite
from .models.content import (
    Question,
    AnswerOption,
    QuestionImageAsset,
    QuestionAudioAsset,
    MultipleChoiceAnswerOption,
    MultipleSelectAnswerOption,
    TypeInAnswerOption,
    OrderAnswerOption,
    RelateAnswerOption,
)
from .models.areas_of_knowledge import AreaOfKnowledge


class AreaOfKnowledgeResource(TranslatableModelResource):
    language_code = Field(
        attribute='_current_language'
    )

    name = Field(
        attribute='name'
    )

    class Meta:
        model = AreaOfKnowledge
        skip_unchanged = True
        report_skipped = False

        import_id_fields = ('id', )

class TopicResource(TranslatableModelResource):
    language_code = Field(
        attribute='_current_language'
    )

    name = Field(
        attribute='name'
    )

    parent = Field(
        column_name='parent',
        attribute='parent',
        widget=TranslatableForeignKeyWidget(Topic, 'name')
    )

    class Meta:
        model = Topic
        skip_unchanged = True
        report_skipped = False
        fields = (
            'id',
            'language_code',
            'identifier',
            'name',
            'is_active',
            'parent',
            'video_assistor',
            'area_of_knowledge',
            'standard_topic',
        )

        import_id_fields = ('id', )

class GradeResource(TranslatableModelResource):
    language_code = Field(
        attribute='_current_language'
    )

    name = Field(
        attribute='name'
    )

    class Meta:
        model = Grade
        skip_unchanged = True
        report_skipped = False
        fields = (
            'id',
            'identifier',
            'language_code',
            'name',
            'audience',
            'is_active',
        )

        import_id_fields = ('id', )
       
class TopicGradeResource(ModelResource):
    class Meta:
        model = TopicGrade
        skip_unchanged = True
        report_skipped = False
        fields = (
            'id',
            'identifier',
            'topic',
            'grade',
            'is_active',
        )
        export_order = (
            'id',
            'identifier',
            'topic',
            'grade',
            'is_active'
        )

        import_id_fields = ('id', )

class QuestionResource(TranslatableModelResource):
    language_code = Field(
        attribute='_current_language'
    )

    question_text = Field(attribute='question_text')

    class Meta:
        model = Question
        skip_unchanged = True
        report_skipped = False
        # use_bulk = True
        field = (
            'id',
            'identifier',
            'language_code',
            'question_text',
            'topic',
            'grade',
        )
        export_order = (
            'id',
            'identifier',
            'language_code',
            'question_text',
            'topic',
            'grade',
        )
        exclude = (
            'is_active',
            'random_slug',
            'deleted_timestamp',
            'create_timestamp',
            'update_timestamp',
            'topic_grade',
        )

        import_id_fields = ('id', )

class QuestionImageAssetResource(ModelResource):
    class Meta:
        model = QuestionImageAsset
        skip_unchanged = True
        report_skipped = False
        fields = (
            'id',
            'identifier',
            'question',
            'order',
            'image'
        )
        export_order = (
            'id',
            'identifier',
            'question',
            'order',
            'image'
        )

        import_id_fields = ('id', )

class MultipleChoiceAnswerOptionResource(TranslatableModelResource):
    language_code = Field(
        attribute='_current_language'
    )

    answer_text = Field(
        attribute='answer_text'
    )
    image = Field(
        attribute='image'
    )
    audio_file = Field(
        attribute='audio_file'
    )
    video = Field(
        attribute='video'
    )
    explanation = Field(
        attribute='explanation'
    )

    class Meta:
        model = MultipleChoiceAnswerOption
        skip_unchanged = True
        report_skipped = False
        fields = (
            'id',
            'identifier',
            'language_code',
            'answer_text',
            'question',
            'is_correct',
            'image',
            'audio_file',
            'video',
            'explanation',
        )
        export_order = (
            'id',
            'identifier',
            'language_code',
            'answer_text',
            'question',
            'is_correct',
            'image',
            'audio_file',
            'video',
            'explanation',
        )
        exclude = (
            'create_timestamp',
            'update_timestamp',
            'random_slug',
        )

        import_id_fields = ('id', )

class MultipleSelectAnswerOptionResource(TranslatableModelResource):
    language_code = Field(
        attribute='_current_language'
    )

    answer_text = Field(
        attribute='answer_text'
    )
    image = Field(
        attribute='image'
    )
    audio_file = Field(
        attribute='audio_file'
    )
    video = Field(
        attribute='video'
    )
    explanation = Field(
        attribute='explanation'
    )
    class Meta:
        model = MultipleSelectAnswerOption
        skip_unchanged = True
        report_skipped = False
        fields = (
            'id',
            'identifier',
            'language_code',
            'answer_text',
            'question',
            'is_correct',
            'image',
            'audio_file',
            'video',
            'explanation',
        )
        export_order = (
            'id',
            'identifier',
            'language_code',
            'answer_text',
            'question',
            'is_correct',
            'image',
            'audio_file',
            'video',
            'explanation',
        )
        exclude = (
            'create_timestamp',
            'update_timestamp',
            'random_slug',
        )

        import_id_fields = ('id', )

class TypeInAnswerOptionResource(TranslatableModelResource):
    language_code = Field(
        attribute='_current_language'
    )

    answer_text = Field(
        attribute='answer_text'
    )

    class Meta:
        model = TypeInAnswerOption
        skip_unchanged = True
        report_skipped = False
        fields = (
            'id',
            'identifier',
            'language_code',
            'answer_text',
            'question',
            'is_correct',
            'case_sensitive',
        )
        export_order = (
            'id',
            'identifier',
            'language_code',
            'answer_text',
            'question',
            'is_correct',
            'case_sensitive',
        )
        exclude = (
            'create_timestamp',
            'update_timestamp',
            'random_slug',
        )

        import_id_fields = ('id', )

class OrderAnswerOptionResource(TranslatableModelResource):
    language_code = Field(
        attribute='_current_language'
    )

    answer_text = Field(
        attribute='answer_text'
    )

    class Meta:
        model = OrderAnswerOption
        skip_unchanged = True
        report_skipped = False
        fields = (
            'id',
            'identifier',
            'language_code',
            'answer_text',
            'question',
            'order',
            'is_correct',
        )
        export_order = (
            'id',
            'identifier',
            'language_code',
            'answer_text',
            'question',
            'order',
            'is_correct',
        )
        exclude = (
            'create_timestamp',
            'update_timestamp',
            'random_slug',
        )

        import_id_fields = ('id', )

class RelateAnswerOptionResource(TranslatableModelResource):
    language_code = Field(
        attribute='_current_language'
    )

    key = Field(
        attribute='key'
    )

    value = Field(
        attribute='value'
    )

    is_correct = ForeignKeyWidget(AnswerOption, 'is_correct')

    class Meta:
        model = RelateAnswerOption
        skip_unchanged = True
        report_skipped = False
        fields = (
            'id',
            'identifier',
            'language_code',
            'key',
            'value',
            'question',
            'is_correct',
        )
        export_order = (
            'id',
            'identifier',
            'language_code',
            'key',
            'value',
            'question',
            'is_correct',
        )
        exclude = (
            'create_timestamp',
            'update_timestamp',
            'random_slug',
        )

        import_id_fields = ('id', )

class AnswerOptionResource(TranslatableModelResource):
    language_code = Field(
        attribute='_current_language'
    )

    answer_text = Field(
        attribute='answer_text'
    )

    class Meta:
        model = AnswerOption
        skip_unchanged = True
        report_skipped = False
        fields = (
            'id',
            'identifier',
            'language_code',
            'answer_text',
            'question',
            'is_correct',
        )
        export_order = (
            'id',
            'identifier',
            'language_code',
            'answer_text',
            'question',
            'is_correct',
        )
        exclude = (
            'create_timestamp',
            'update_timestamp',
            'random_slug',
        )

        import_id_fields = ('id', )

class QuestionAudioAssetResource(ModelResource):
    class Meta:
        model = QuestionAudioAsset
        skip_unchanged = True
        report_skipped = False
        fields = (
            'id',
            'identifier',
            'question',
            'order',
            'audio_file'
        )
        export_order = (
            'id',
            'identifier',
            'question',
            'order',
            'audio_file'
        )

        import_id_fields = ('id', )

class PrerequisiteResource(ModelResource):
    class Meta:
        model = Prerequisite
        skip_unchanged = True
        report_skipped = False
        fields = ['id', 'topic', 'prerequisites', 'identifier']

        import_id_fields = ('id', )

class GradePrerequisiteResource(ModelResource):
    class Meta:
        model = GradePrerequisite
        skip_unchanged = True
        report_skipped = False
        fields = [
            'id',
            'identifier',
            'area_of_knowledge',
            'grade',
            'mastery',
            'competence',
        ]

        import_id_fields = ('id', )
