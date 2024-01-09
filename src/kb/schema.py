import random
from unittest import result
import graphene
from django.conf import settings
from django.utils.html import strip_tags
from graphene_django import DjangoObjectType
from kb.models import AreaOfKnowledge, Grade, Topic, TopicGrade, Prerequisite
from kb.models.content import Question, AnswerOption
from kb.models.content import (
    MultipleChoiceAnswerOption,
    MultipleSelectAnswerOption,
    TypeInAnswerOption,
    OrderAnswerOption,
    RelateAnswerOption
)
from kb.models.content import QuestionImageAsset, QuestionAudioAsset, QuestionVideoAsset, QuestionTTSAsset
from engine.models import TopicStudentReport
from engine.schema import TopicStudentReportSchema
from students.models import StudentTopicMastery
from django.db.models import Q

class AreaOfKnowledgeSchema(DjangoObjectType):
    class Meta:
        model = AreaOfKnowledge
        fields = "__all__"

    name = graphene.String()

    def resolve_name(self, info, language_code=None):
        try:
            current_language = info.context.user.language
        except AttributeError:
            current_language = settings.LANGUAGE_CODE

        return self.safe_translation_getter(
            "name", language_code=current_language)


class GradeSchema(DjangoObjectType):
    class Meta:
        model = Grade
        fields = "__all__"

    name = graphene.String()

    def resolve_name(self, info, language_code=None):
        try:
            current_language = info.context.user.language
        except AttributeError:
            current_language = settings.LANGUAGE_CODE

        return self.safe_translation_getter(
            "name", language_code=current_language)


class TopicSchema(DjangoObjectType):
    class Meta:
        model = Topic
        fields = "__all__"

    name = graphene.String()
    report = graphene.Field(
        TopicStudentReportSchema,
        student=graphene.ID()
    )
    mastery = graphene.String(
        student=graphene.ID()
    )
    sub_topics_by_grade = graphene.List(
        'kb.schema.TopicSchema',
        grade_id=graphene.ID()
    )
    def resolve_name(self, info, language_code=None):
        try:
            current_language = info.context.user.language
        except AttributeError:
            current_language = settings.LANGUAGE_CODE

        # return self.safe_translation_getter(
        #     "name", language_code=current_language)
        return self.safe_translation_getter(
            "name", any_language=True)

    def resolve_report(self, info, student=None):
        if student is None:
            student = info.context.user.student
        try:
            report = TopicStudentReport.objects.get(
                topic=self,
                student=student,
            )
        except TopicStudentReport.DoesNotExist:
            report = None
        return report

    def resolve_mastery(self, info, student=None):
        if student is None:
            student = info.context.user.student
        try:
            mastery = StudentTopicMastery.objects.get(
                topic=self,
                student=student,
            ).mastery_level
        except StudentTopicMastery.DoesNotExist:
            mastery = None
        return mastery
    def resolve_sub_topics_by_grade(self, info, grade_id):
        return self.sub_topics.all().filter(topicgrade__grade__id=grade_id)


class TopicGradeSchema(DjangoObjectType):
    class Meta:
        model = TopicGrade
        fields = "__all__"


class PrerequisiteSchema(DjangoObjectType):
    class Meta:
        model = Prerequisite
        fields = "__all__"


class QuestionImageAssetSchema(DjangoObjectType):
    class Meta:
        model = QuestionImageAsset
        fields = "__all__"


class QuestionAudioAssetSchema(DjangoObjectType):
    class Meta:
        model = QuestionAudioAsset
        fields = "__all__"


class QuestionVideoAssetSchema(DjangoObjectType):
    class Meta:
        model = QuestionVideoAsset
        fields = "__all__"


class QuestionTTSAssetSchema(DjangoObjectType):
    class Meta:
        model = QuestionTTSAsset
        fields = "__all__"


class QuestionSchema(DjangoObjectType):
    class Meta:
        model = Question
        fields = "__all__"

    question_text = graphene.String()
    question_image_assets = graphene.List(QuestionImageAssetSchema)
    question_audio_assets = graphene.List(QuestionAudioAssetSchema)
    question_video_assets = graphene.List(QuestionVideoAssetSchema)

    question_audio_url = graphene.String()
    answer_options = graphene.List('kb.schema.AnswerOptionUnionSchema')

    def resolve_question_text(self, info, language_code=None):
        # return strip_tags(self.safe_translation_getter("question_text", any_language=True))
        return self.safe_translation_getter("question_text", any_language=True)

    def resolve_question_image_assets(self, info):
        return self.get_questionimageasset_set()

    def resolve_question_audio_assets(self, info):
        return self.get_questionaudioasset_set()

    def resolve_question_video_assets(self, info):
        return self.get_questionvideoasset_set()

    def resolve_question_audio_url(self, info):
        language = self.get_available_languages()[0]
        try:
            tts_file = self.get_questionttsasset(language).tts_file.url
            if not tts_file:
                raise Exception("tts_file is empty")
            tts_string = f'{settings.DOMAIN}{tts_file}'
        except Exception as e:
            print(e)
            try:
                # self.save_gtts()
                tts_file = self.get_questionttsasset(language).tts_file.url
                tts_string = f'{settings.DOMAIN}{tts_file}'
            except Exception as e:
                tts_string = None

        return tts_string

    def resolve_answer_options(self, info):
        return self.answeroption_set.all()


class AnswerOptionInterface(graphene.Interface):
    id = graphene.ID()
    question = graphene.Field(QuestionSchema)
    is_correct = graphene.Boolean()
    answer_audio_url = graphene.String()

    def resolve_answer_audio_url(self, info):
        language = self.get_available_languages()[0]
        try:
            tts_file = self.get_answeroptionttsasset(language).tts_file.url
            if not tts_file:
                raise Exception("tts_file is empty")
            tts_string = f'{settings.DOMAIN}{tts_file}'
        except Exception as e:
            print(e)
            try:
                # self.save_gtts()
                tts_file = self.get_answeroptionttsasset(language).tts_file.url
                tts_string = f'{settings.DOMAIN}{tts_file}'
            except Exception as e:
                tts_string = None

        return tts_string

class AnswerOptionSchema(DjangoObjectType):
    class Meta:
        model = AnswerOption
        interfaces = (AnswerOptionInterface,)
        fields = "__all__"

class MultipleChoiceAnswerOptionSchema(DjangoObjectType):
    class Meta:
        model = MultipleChoiceAnswerOption
        fields = "__all__"
        interfaces = (AnswerOptionInterface,)

    answer_text = graphene.String()
    explanation = graphene.String()
    image = graphene.String()
    audio_file = graphene.String()
    video = graphene.String()
    test  = graphene.String()

    def resolve_test(self, info):
        return "asre"

    def resolve_answer_text(self, info, language_code=None):
        return self.safe_translation_getter("answer_text", any_language=True)

    def resolve_image(self, info, language_code=None):
        try:
            current_language = info.context.user.language
        except AttributeError:
            current_language = settings.LANGUAGE_CODE

        return self.safe_translation_getter(
            "image", language_code=current_language)

    def resolve_explanation(self, info, language_code=None):
        try:
            current_language = info.context.user.language
        except AttributeError:
            current_language = settings.LANGUAGE_CODE

        return self.safe_translation_getter(
            "explanation", language_code=current_language)

    def resolve_audio_file(self, info, language_code=None):
        try:
            current_language = info.context.user.language
        except AttributeError:
            current_language = settings.LANGUAGE_CODE

        return self.safe_translation_getter(
            "audio_file", language_code=current_language)

    def resolve_video(self, info, language_code=None):
        try:
            current_language = info.context.user.language
        except AttributeError:
            current_language = settings.LANGUAGE_CODE

        return self.safe_translation_getter(
            "video", language_code=current_language)

class MultipleSelectAnswerOptionSchema(DjangoObjectType):
    class Meta:
        model = MultipleSelectAnswerOption
        fields = "__all__"
        interfaces = (AnswerOptionInterface,)

    answer_text = graphene.String()
    explanation = graphene.String()
    image = graphene.String()
    audio_file = graphene.String()
    video = graphene.String()

    def resolve_answer_text(self, info, language_code=None):
        return self.safe_translation_getter("answer_text", any_language=True)

    def resolve_image(self, info, language_code=None):
        try:
            current_language = info.context.user.language
        except AttributeError:
            current_language = settings.LANGUAGE_CODE

        return self.safe_translation_getter(
            "image", language_code=current_language)

    def resolve_explanation(self, info, language_code=None):
        try:
            current_language = info.context.user.language
        except AttributeError:
            current_language = settings.LANGUAGE_CODE

        return self.safe_translation_getter(
            "explanation", language_code=current_language)

    def resolve_audio_file(self, info, language_code=None):
        try:
            current_language = info.context.user.language
        except AttributeError:
            current_language = settings.LANGUAGE_CODE

        return self.safe_translation_getter(
            "audio_file", language_code=current_language)

    def resolve_video(self, info, language_code=None):
        try:
            current_language = info.context.user.language
        except AttributeError:
            current_language = settings.LANGUAGE_CODE

        return self.safe_translation_getter(
            "video", language_code=current_language)

class TypeInAnswerOptionSchema(DjangoObjectType):
    class Meta:
        model = TypeInAnswerOption
        fields = "__all__"
        interfaces = (AnswerOptionInterface,)

    answer_text = graphene.String()
    explanation = graphene.String()
    image = graphene.String()
    audio_file = graphene.String()
    video = graphene.String()

    def resolve_answer_text(self, info, language_code=None):
        try:
            current_language = info.context.user.language
        except AttributeError:
            current_language = settings.LANGUAGE_CODE

        return self.safe_translation_getter(
            "answer_text", language_code=current_language)

    def resolve_image(self, info, language_code=None):
        try:
            current_language = info.context.user.language
        except AttributeError:
            current_language = settings.LANGUAGE_CODE

        return self.safe_translation_getter(
            "image", language_code=current_language)

    def resolve_explanation(self, info, language_code=None):
        try:
            current_language = info.context.user.language
        except AttributeError:
            current_language = settings.LANGUAGE_CODE

        return self.safe_translation_getter(
            "explanation", language_code=current_language)

    def resolve_audio_file(self, info, language_code=None):
        try:
            current_language = info.context.user.language
        except AttributeError:
            current_language = settings.LANGUAGE_CODE

        return self.safe_translation_getter(
            "audio_file", language_code=current_language)

    def resolve_video(self, info, language_code=None):
        try:
            current_language = info.context.user.language
        except AttributeError:
            current_language = settings.LANGUAGE_CODE

        return self.safe_translation_getter(
            "video", language_code=current_language)

class OrderAnswerOptionSchema(DjangoObjectType):
    class Meta:
        model = OrderAnswerOption
        fields = "__all__"
        interfaces = (AnswerOptionInterface,)

    answer_text = graphene.String()
    image = graphene.String()
    audio_file = graphene.String()
    video = graphene.String()

    def resolve_answer_text(self, info, language_code=None):
        try:
            current_language = info.context.user.language
        except AttributeError:
            current_language = settings.LANGUAGE_CODE

        return self.safe_translation_getter(
            "answer_text", language_code=current_language)

    def resolve_image(self, info, language_code=None):
        try:
            current_language = info.context.user.language
        except AttributeError:
            current_language = settings.LANGUAGE_CODE

        return self.safe_translation_getter(
            "image", language_code=current_language)

    def resolve_audio_file(self, info, language_code=None):
        try:
            current_language = info.context.user.language
        except AttributeError:
            current_language = settings.LANGUAGE_CODE

        return self.safe_translation_getter(
            "audio_file", language_code=current_language)

    def resolve_video(self, info, language_code=None):
        try:
            current_language = info.context.user.language
        except AttributeError:
            current_language = settings.LANGUAGE_CODE

        return self.safe_translation_getter(
            "video", language_code=current_language)

class RelateAnswerOptionSchema(DjangoObjectType):
    class Meta:
        model = RelateAnswerOption
        fields = "__all__"
        interfaces = (AnswerOptionInterface,)

    key = graphene.String()
    key_image = graphene.String()
    value = graphene.String()
    value_image = graphene.String()

    def resolve_key(self, info, language_code=None):
        try:
            current_language = info.context.user.language
        except AttributeError:
            current_language = settings.LANGUAGE_CODE

        return self.safe_translation_getter(
            "key", language_code=current_language)

    def resolve_key_image(self, info, language_code=None):
        try:
            current_language = info.context.user.language
        except AttributeError:
            current_language = settings.LANGUAGE_CODE

        return self.safe_translation_getter(
            "key_image", language_code=current_language)

    def resolve_value(self, info, language_code=None):
        try:
            current_language = info.context.user.language
        except AttributeError:
            current_language = settings.LANGUAGE_CODE

        return self.safe_translation_getter(
            "value", language_code=current_language)

    def resolve_value_image(self, info, language_code=None):
        try:
            current_language = info.context.user.language
        except AttributeError:
            current_language = settings.LANGUAGE_CODE

        return self.safe_translation_getter(
            "value_image", language_code=current_language)


class AnswerOptionUnionSchema(graphene.Union):
    @classmethod
    def resolve_type(cls, instance, info):

        if isinstance(instance, MultipleChoiceAnswerOption):
            return MultipleChoiceAnswerOptionSchema

        elif isinstance(instance, MultipleSelectAnswerOption):
            return MultipleSelectAnswerOptionSchema

        elif isinstance(instance, TypeInAnswerOption):
            return TypeInAnswerOptionSchema

        elif isinstance(instance, OrderAnswerOption):
            return OrderAnswerOptionSchema

        elif isinstance(instance, RelateAnswerOption):
            return RelateAnswerOptionSchema

        return None

    class Meta:

        types = [MultipleChoiceAnswerOptionSchema, MultipleSelectAnswerOptionSchema, TypeInAnswerOptionSchema, OrderAnswerOptionSchema, RelateAnswerOptionSchema]


class RandomQuesionsType(graphene.ObjectType):
    questions = graphene.List(QuestionSchema)
    total = graphene.Int()

class Query(graphene.ObjectType):
    # ----------------- AreaOfKnowledge ----------------- #

    areas_of_knowledge = graphene.List(AreaOfKnowledgeSchema)
    area_of_knowledge_by_id = graphene.Field(
        AreaOfKnowledgeSchema, id=graphene.ID())
    areas_of_knowledge_by_audience = graphene.List(
        AreaOfKnowledgeSchema, audience=graphene.ID())

    def resolve_areas_of_knowledge(root, info, **kwargs):
        # Querying a list
        return AreaOfKnowledge.objects.all()

    def resolve_area_of_knowledge_by_id(root, info, id):
        # Querying a single AoK
        return AreaOfKnowledge.objects.get(pk=id)

    def resolve_areas_of_knowledge_by_audience(root, info, audience):
        # Querying a list of AoKs filtered by audience
        return AreaOfKnowledge.objects.filter(audience=audience)

    # ----------------- Grade ----------------- #

    grades = graphene.List(GradeSchema)
    grade = graphene.Field(GradeSchema, id=graphene.String())

    def resolve_grades(root, info, **kwargs):
        # Querying a list
        return Grade.objects.all()

    def resolve_grade(root, info, id):
        # Querying a single question
        return Grade.objects.get(pk=id)

    # ----------------- Topic ----------------- #

    topics = graphene.List(TopicSchema)
    topic_by_id = graphene.Field(TopicSchema, id=graphene.ID())
    topics_by_aok = graphene.List(TopicSchema, aok_id=graphene.ID())
    topics_by_aok_and_grade = graphene.List(TopicSchema, aok_id=graphene.ID(), grade_id=graphene.ID())
    root_topics = graphene.List(TopicSchema)
    root_topics_by_aok = graphene.List(TopicSchema, aok_id=graphene.ID())
    root_topics_by_aok_and_grade = graphene.List(TopicSchema, aok_id=graphene.ID(), grade_id=graphene.ID())
    topic_random_questions = graphene.Field(RandomQuesionsType, topic_id=graphene.ID(), count=graphene.Int())

    def resolve_topic_random_questions(root, info, topic_id, count):

        result=RandomQuesionsType()
        topic_quesions = Question.objects.filter(topic=topic_id, is_active=True)
        # total_count = topic_quesions.count()
        # if total_count < 5:
        #     random_set = topic_quesions
        # else:
            # valid_profiles_id_list = ProfilePage.objects.filter(profileisbannedis=False).values_list('id', flat=True)
            # random_profiles_id_list = random.sample(valid_profiles_id_list, min(len(valid_profiles_id_list), 10))
            # query_set = ProfilePage.objects.filter(id__in=random_profiles_id_list)
        valid_quesion_id_list = Question.objects.filter(topic=topic_id, is_active=True).values_list('id', flat=True)
        random_questions_id_list = random.sample(list(valid_quesion_id_list), min(len(valid_quesion_id_list), count))
        result.questions = Question.objects.filter(id__in=random_questions_id_list)
        result.total=len(valid_quesion_id_list)
        return result


    def resolve_topics(root, info, **kwargs):
        # Querying a list
        return Topic.objects.all()

    def resolve_topic_by_id(root, info, id):
        # Querying a single question
        return Topic.objects.get(pk=id)
    
    def resolve_topics_by_aok(root, info, aok_id):
        return Topic.objects.filter(
            area_of_knowledge=aok_id
        )

    def resolve_topics_by_aok_and_grade(root, info, aok_id, grade_id):
        return Topic.objects.filter(
            area_of_knowledge=aok_id,
        ).filter(
            # Q(topicgrade__grade__id=grade_id) | Q(level=0)
            topicgrade__grade__id=grade_id
        )
    
    def resolve_root_topics(root, info):
        return Topic.objects.filter(level=0)

    def resolve_root_topics_by_aok(root, info, aok_id):
        return Topic.objects.filter(
            parent__isnull=True,
            area_of_knowledge=aok_id
        )
    def resolve_root_topics_by_aok_and_grade(root, info, aok_id, grade_id):
        return Topic.objects.filter(
            parent__isnull=True,
            area_of_knowledge=aok_id,
            # topicgrade__grade__id=grade_id
        )

    # ----------------- TopicGrade ----------------- #

    topics_grade = graphene.List(TopicGradeSchema)
    topic_grade_by_id = graphene.Field(TopicGradeSchema, id=graphene.String())

    def resolve_topics_grade(root, info, **kwargs):
        # Querying a list
        return TopicGrade.objects.all()

    def resolve_topic_grade_by_id(root, info, id):
        # Querying a single question
        return TopicGrade.objects.get(pk=id)

    # ----------------- Prerequisite ----------------- #

    prerequisites = graphene.List(PrerequisiteSchema)
    prerequisite_by_id = graphene.Field(
        PrerequisiteSchema, id=graphene.String())

    def resolve_prerequisites(root, info, **kwargs):
        # Querying a list
        return Prerequisite.objects.all()

    def resolve_prerequisite_by_id(root, info, id):
        # Querying a single question
        return Prerequisite.objects.get(pk=id)

    # ----------------- Question ----------------- #

    questions = graphene.List(QuestionSchema)
    question_by_id = graphene.Field(QuestionSchema, id=graphene.ID())

    def resolve_questions(root, info, **kwargs):
        # Querying a list
        return Question.objects.all()

    def resolve_question_by_id(root, info, id):
        # Querying a single question
        return Question.objects.get(pk=id)

    # ----------------- QuestionImageAsset ----------------- #

    question_image_assets = graphene.List(QuestionImageAssetSchema)
    question_image_asset_by_id = graphene.Field(
        QuestionImageAssetSchema, id=graphene.ID())

    def resolve_question_image_assets(root, info, **kwargs):
        # Querying a list
        return QuestionImageAsset.objects.all()

    def resolve_question_image_asset_by_id(root, info, id):
        # Querying a single question
        return QuestionImageAsset.objects.get(pk=id)

    # ----------------- AnswerOption ----------------- #

    answers_option = graphene.List(AnswerOptionUnionSchema)
    answers_option_by_id = graphene.Field(
        AnswerOptionUnionSchema, id=graphene.ID())

    def resolve_answers_option(root, info, **kwargs):
        # Querying a list
        return AnswerOption.objects.all()

    def resolve_answers_option_by_id(root, info, id):
        # Querying a single question
        return AnswerOption.objects.get(pk=id)
