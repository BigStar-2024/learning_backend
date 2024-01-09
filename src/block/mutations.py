from itertools import cycle, islice
import graphene
import random
from django.utils import timezone
from django.db.models import F
from kb.models.grades import Grade
from students.schema import StudentSchema
from .models import (
    BlockPresentation,
    Block,
    BlockTransaction,
    BlockQuestionPresentation,
    StudentBlockQuestionPresentationHistory
)
from .schema import BlockPresentationSchema
from students.models import StudentHomework, StudentTopicMastery, StudentTopicStatus, Student
from kb.models import Topic, TopicGrade, AreaOfKnowledge
from kb.models.content import AnswerOption, Question
from kb.models.content import (
    MultipleChoiceAnswerOption,
    MultipleSelectAnswerOption,
    TypeInAnswerOption,
    OrderAnswerOption,
    RelateAnswerOption
)
from engine.models import TopicStudentReport, AreaOfKnowledgeStudentReport
from experiences.models import Battery
from decimal import Decimal
from wallets.models import CoinWallet
from django.db.models import Q, Count


class RelateAnswerOptionInput(graphene.InputObjectType):
    key = graphene.String()
    value = graphene.String()


class TypeInAnswerOptionInput(graphene.InputObjectType):
    answer_option = graphene.ID()
    typed_answer = graphene.String()


class BlockQuestionInput(graphene.InputObjectType):
    question = graphene.ID()
    multiple_choice_answer_option = graphene.ID()
    multiple_select_answer_options = graphene.List(graphene.ID)
    type_in_answer_option = TypeInAnswerOptionInput()
    order_answer_options = graphene.List(graphene.String)
    relate_answer_options = graphene.List(RelateAnswerOptionInput)


class CreatePathBlockPresentation(graphene.Mutation):
    block_presentation = graphene.Field(BlockPresentationSchema)

    class Arguments:
        student_id = graphene.ID(required=True)
        topic_id = graphene.ID(required=True)

    def mutate(self, info, student_id, topic_id):
        user = info.context.user

        if not user.is_authenticated:
            raise Exception("Authentication credentials were not provided")
        if not user.student:
            raise Exception("Not found student")

        student = user.student

        try:
            topic_grade = TopicGrade.objects.get(topic=topic_id)
        except Topic.DoesNotExist:
            raise Exception("Topic does not exist")

        # Create block if it doesn't exist
        block, new = Block.objects.get_or_create(
            topic_grade=topic_grade,
            modality='PATH',
        )
        block.students.add(student)
        block.save()
        if block.questions.all().count() == 0:
            available_question_query_set = (Question.objects
                                            .filter(topic=topic_grade.topic)
                                            .filter(grade=topic_grade.grade)
                                            # .filter(answeroption__len__gt=0)
                                            .annotate(answeroption_count=Count('answeroption'))
                                            .filter(answeroption_count__gt=0))
            available_questions = list(
                available_question_query_set
            )
            # for question in available_questions:
            #     print("count is ",available_questions.answeroption_count)

            if (len(available_questions) < 1):
                raise Exception(
                    "Topic " + f'{topic_grade.topic.id}' + " hasn't questions which has answers")

            # This part caused infinite loop error in case the len < block.block_size, also not necessary
            # while len(available_questions) < block.block_size:
            #     for question in available_questions:
            #         available_questions.add(question)

            # generate random questions for block_size
            random_questions = random.sample(
                list(islice(cycle(available_questions), block.block_size)), block.block_size
            )
            for question in random_questions:
                block.questions.add(question)
            block.save()
        # Create block presentation for block
        block_presentation, new = BlockPresentation.objects.get_or_create(
            block=block,
            student=student,
        )
        block_presentation.save()

        return CreatePathBlockPresentation(
            block_presentation=block_presentation)


class CreateHomeworkBlockPresentation(graphene.Mutation):
    block_presentation = graphene.Field(BlockPresentationSchema)

    class Arguments:
        student_homework_id = graphene.ID(required=True)

    def mutate(self, info, student_homework_id):
        user = info.context.user

        if not user.is_authenticated:
            raise Exception("Authentication credentials were not provided")
        if not user.student:
            raise Exception("Not found student")
        now = timezone.now()

        student = user.student

        student_homework = StudentHomework.objects.get(pk=student_homework_id)
        if (student_homework.student != student):
            raise Exception("This homework is not yours!")
        if (student_homework.start_at > now):
            raise Exception(
                f"You can start this homework at {student_homework.start_at}")
        if ((student_homework.end_at is not None) and (student_homework.end_at) < now):
            student_homework.status = "Expired"
            student_homework.save()
            # student_homework.delete()
            raise Exception(
                f"You should finish this homework at {student_homework.end_at}. But time has passed!")

        topic = student_homework.topic

        try:
            topic_grade = TopicGrade.objects.get(topic=topic)
        except Topic.DoesNotExist:
            raise Exception("Topic does not exist")

        # Create block if it doesn't exist
        block, new = Block.objects.get_or_create(
            topic_grade=topic_grade,
            modality='HOMEWORK',
            student_homework=student_homework,
            block_size=student_homework.number_of_questions
        )
        block.students.add(student)
        block.save()
        if block.questions.all().count() == 0:
            available_question_query_set = (Question.objects
                                            .filter(topic=topic_grade.topic)
                                            .filter(grade=topic_grade.grade)
                                            # .filter(answeroption__len__gt=0)
                                            .annotate(answeroption_count=Count('answeroption'))
                                            .filter(answeroption_count__gt=0))
            available_questions = list(
                available_question_query_set
            )
            # for question in available_questions:
            #     print("count is ",available_questions.answeroption_count)

            if (len(available_questions) < 1):
                raise Exception(
                    "Topic " + f'{topic_grade.topic.id}' + " hasn't questions which has answers")

            # This part caused infinite loop error in case the len < block.block_size, also not necessary
            # while len(available_questions) < block.block_size:
            #     print(len(available_questions))

            #     for question in available_questions:
            #         available_questions.add(question)

            # generate random questions for block_size
            random_questions = random.sample(
                list(islice(cycle(available_questions), block.block_size)), block.block_size
            )

            for question in random_questions:
                block.questions.add(question)
            block.save()
        # Create block presentation for block
        block_presentation, new = BlockPresentation.objects.get_or_create(
            block=block,
            student=student,
        )
        block_presentation.save()

        return CreatePathBlockPresentation(
            block_presentation=block_presentation)


class CreateAIBlockPresentation(graphene.Mutation):
    block_presentation = graphene.Field(BlockPresentationSchema)

    class Arguments:
        student_id = graphene.ID()
        aok_id = graphene.ID(required=True)

    def mutate(self, info, aok_id, student_id=None):
        if student_id is None:
            user = info.context.user

            if not user.is_authenticated:
                raise Exception("Authentication credentials were not provided")
            if not user.student:
                raise Exception("Not found student")

            student = user.student
        else:
            student = Student.objects.get(id=student_id)
        if (student.classroom is None and len(student.guardianstudentplan.subject.filter(pk=aok_id)) < 1):
            raise Exception(
                "You don't have correct permission to use this subject")

        # Define weights for status and mastery
        mastery_weights = {'NP': 50, 'N': 30, 'C': 20, 'M': 0}
        status_weights = {'B': 0, 'P': 20, 'A': 80}

        # Find a topic given the AoK
        try:
            area_of_knowledge = AreaOfKnowledge.objects.get(id=aok_id)
        except AreaOfKnowledge.DoesNotExist:
            raise Exception("Area of knowledge does not exist")

        # get all leafs - topics
        topics = area_of_knowledge.topic_set.all().filter(lft=F("rght") - 1)

        if student.grade is None:
            raise Exception('This student has not grade information')
            
        student_grade_name = student.grade.name
        grades_with_same_name = Grade.objects.filter(
            translations__language_code="en-us",
            translations__name=student_grade_name
        )
        qs1 = StudentTopicStatus.objects.filter(
            student=student,
            topic__in=topics,
            topic__topicgrade__grade__in=grades_with_same_name,
        )
        # qs1 = StudentTopicStatus.objects.filter(
        #     student=student,
        #     topic__in=topics,
        # )

        if (len(qs1) < 1):
            student.init_student_topic_mastery_specific_aok(aok_id=aok_id)
            student.init_student_topic_status_specific_aok(aok_id=aok_id)
            qs1 = StudentTopicStatus.objects.filter(
                student=student,
                topic__in=topics,
            )

        available_status = [
            status['status'] for status in qs1.values('status').distinct()
        ]

        available_status_weights = [
            status_weights[status] for status in available_status
        ]

        status_selection = random.choices(
            population=available_status,
            weights=available_status_weights,
        )[0]

        qs1 = qs1.filter(status=status_selection).values('topic')

        qs2 = StudentTopicMastery.objects.filter(
            student=student,
            topic__in=[topic['topic'] for topic in qs1],
        )

        available_mastery = [mastery['mastery_level']
                             for mastery in qs2.values('mastery_level').distinct()]

        available_mastery_weights = [
            mastery_weights[mastery] for mastery in available_mastery
        ]

        mastery_selection = random.choices(
            population=available_mastery,
            weights=available_mastery_weights,
        )[0]

        qs2 = qs2.filter(mastery_level=mastery_selection).values('topic')

        topic_choice = random.choice(qs2)
        selected_topic = Topic.objects.get(id=topic_choice['topic'])
        topic_grade = TopicGrade.objects.filter(topic=selected_topic)
        if (len(topic_grade) < 1):
            raise Exception(
                "Topic " + f'{selected_topic.id}' + " hasn't grade")
        topic_grade = topic_grade[0]

        # Create block if it doesn't exist
        block, created = Block.objects.get_or_create(
            topic_grade=topic_grade,
            modality='AI',
        )
        block.students.add(student)
        block.save()
        if block.questions.all().count() == 0:
            available_question_query_set = (Question.objects
                                            .filter(topic=topic_grade.topic)
                                            .filter(grade=topic_grade.grade)
                                            # .filter(answeroption__len__gt=0)
                                            .annotate(answeroption_count=Count('answeroption'))
                                            .filter(answeroption_count__gt=0))
            available_questions = list(
                available_question_query_set
            )

            if (len(available_questions) < 1):
                raise Exception(
                    "Topic " + f'{topic_grade.topic.id}' + " hasn't questions which has answers")

            # 10 30
            # This part caused infinite loop error in case the len < block.block_size, also not necessary

            # while len(available_questions) < block.block_size:
            #     for question in available_questions:
            #         available_questions.add(question)

            # generate random questions for block_size
            random_questions = random.sample(
                list(islice(cycle(available_questions), block.block_size)), block.block_size
            )
            for question in random_questions:
                block.questions.add(question)
        block.save()

        # Create block presentation for block
        block_presentation, new = BlockPresentation.objects.get_or_create(
            block=block,
            student=student,
        )
        block_presentation.save()

        return CreateAIBlockPresentation(block_presentation=block_presentation)


class CreateBlockPresentationByQuestionId(graphene.Mutation):
    block_presentation = graphene.Field(BlockPresentationSchema)

    class Arguments:
        student_id = graphene.ID()
        question_ids = graphene.List(graphene.ID, required=True)

    def mutate(self, info, question_ids, student_id=None):
        if student_id is None:
            user = info.context.user

            if not user.is_authenticated:
                raise Exception("Authentication credentials were not provided")
            if not user.student:
                raise Exception("Not found student")

            student = user.student
        else:
            student = Student.objects.get(id=student_id)
        questions = Question.objects.filter(
            pk__in=question_ids
        )
        topic = questions.all()[0].topic
        topicGrade = TopicGrade.objects.get(topic=topic)
        # block, new = Block.objects.get_or_create(
        #     topic_grade=topicGrade,
        #     modality='TEST',
        # )
        block = Block.objects.create(
            topic_grade=topicGrade,
            modality='TEST',
        )
        block.students.add(student)
        block.save()

        block.questions.add(*questions)
        block.save()

        # Create block presentation for block
        block_presentation, new = BlockPresentation.objects.get_or_create(
            block=block,
            student=student,
        )
        block_presentation.save()

        return CreateAIBlockPresentation(block_presentation=block_presentation)


class FinishBlockPresentation(graphene.Mutation):
    block_presentation = graphene.Field(BlockPresentationSchema)
    student = graphene.Field(StudentSchema)

    class Arguments:
        block_presentation_id = graphene.ID(required=True)
        hits = graphene.Int(required=True)
        errors = graphene.Int(required=True)
        bonusCoins = graphene.Float(required=True)
        battery_level = graphene.Int(required=True)
        questions = graphene.List(BlockQuestionInput)

    def mutate(
            self,
            info,
            block_presentation_id,
            hits,
            errors,
            bonusCoins,
            battery_level,
            questions):
        user = info.context.user

        if not user.is_authenticated:
            raise Exception("Authentication credentials were not provided")
        if not user.student:
            raise Exception("Not found student")

        student = user.student

        battery, new = Battery.objects.get_or_create(student=student)

        battery.level = battery_level
        battery.save()

        # Assign values to BlockPresentation
        block_presentation = BlockPresentation.objects.get(
            id=block_presentation_id
        )

        block = block_presentation.block

        if block.modality == 'AI':
            incorrect_exp_unit = 1
            correct_exp_unit = 5
            coin_unit = 10 # coins per correct question
            exp = (correct_exp_unit * hits) + \
                (incorrect_exp_unit * errors) + user.student.points
        elif block.modality == 'HOMEWORK':
            incorrect_exp_unit = 0
            correct_exp_unit = 0
            coin_unit = 0
            exp = 0
            student_homework = block.student_homework
            # if the student tried the homework before, return previous results
            if student_homework.status == "Done":
                return FinishBlockPresentation(
                    block_presentation=block_presentation,
                    student=student)
            student_homework.status = "Done"
            student_homework.save()
            # student_homework.delete()
            # student_homework.delete()
        else:
            incorrect_exp_unit = 0
            correct_exp_unit = 0
            coin_unit = 0
            exp = 0

        block_presentation.hits = hits
        block_presentation.errors = errors
        block_presentation.total = hits + errors
        block_presentation.end_timestamp = timezone.now()
        block_presentation.points = exp
        block_presentation.bonusCoins = bonusCoins
        block_presentation.coins = coin_unit * hits
        block_presentation.save()

        # Create registers on BlockQuestionPresentation
        block_topic = block_presentation.block.topic_grade.topic
        block_aok = block_topic.area_of_knowledge

        student_block_question_history = StudentBlockQuestionPresentationHistory.objects.create(
            student=student)
        for question in questions:
            question_object = Question.objects.get(id=question['question'])
            question_type = question_object.question_type
            # answer_object = AnswerOption.objects.get(
            #     id=question['answer_option'])

            block_question_presentation = BlockQuestionPresentation(
                block_presentation=block_presentation,
                question=question_object,
                topic=block_topic,
            )
            block_question_presentation.save()

            if question_type == 'MC':
                answer_option = MultipleChoiceAnswerOption.objects.get(
                    id=question['multiple_choice_answer_option']
                )
                if (answer_option.is_correct):
                    block_question_presentation.status = 'CORRECT'
                else:
                    block_question_presentation.status = 'INCORRECT'
                block_question_presentation.chosen_answer.add(answer_option)
            elif question_type == 'MS':
                block_question_presentation.status = 'CORRECT'
                for answer in question['multiple_select_answer_options']:
                    answer_option = MultipleSelectAnswerOption.objects.get(
                        id=answer
                    )
                    block_question_presentation.chosen_answer.add(
                        answer_option)
                    if (not answer_option.is_correct):
                        block_question_presentation.status = 'INCORRECT'
            elif question_type == 'T':
                is_correct = True
                answer_text = question['type_in_answer_option']['typed_answer']
                correct_answer_id = question['type_in_answer_option']['answer_option']
                correct_answer = TypeInAnswerOption.objects.get(
                    id=correct_answer_id
                )

                if correct_answer.case_sensitive:
                    if answer_text == correct_answer.answer_text:
                        is_correct = True
                    else:
                        is_correct = False
                else:
                    if answer_text.casefold() == correct_answer.answer_text.casefold():
                        is_correct = True
                    else:
                        is_correct = False

                block_question_presentation.typed_answer = answer_text
                block_question_presentation.save()
                if is_correct:
                    block_question_presentation.status = 'CORRECT'
                else:
                    block_question_presentation.status = 'INCORRECT'
            elif question_type == 'O':
                answer_options = question['order_answer_options']
                block_question_presentation.status = 'CORRECT'
                for order, answer_option in enumerate(answer_options):
                    order_answer_option = OrderAnswerOption.objects.filter(
                        question=question_object,
                        translations__answer_text=answer_option,
                    )[0]
                    if (order_answer_option.order != order + 1):
                        block_question_presentation.status = 'INCORRECT'
                    # order_answer_option.answer_text = answer_option
                    # order_answer_option.save()
                    block_question_presentation.chosen_answer.add(
                        order_answer_option
                    )
            elif question_type == 'R':
                answer_options = question['relate_answer_options']
                block_question_presentation.status = 'CORRECT'
                if len(answer_options) < 1:
                    block_question_presentation.status = 'INCORRECT'
                for answer_option in answer_options:
                    relate_answer_options = RelateAnswerOption.objects.filter(
                        question=question_object,
                        translations__key=answer_option['key'],
                        translations__value=answer_option['value'],
                    )
                    if (len(relate_answer_options) < 1):
                        block_question_presentation.status = 'INCORRECT'
            block_question_presentation.save()
            student_block_question_history.block_question_presentation.add(
                block_question_presentation)
        student_block_question_history.save()

        # Create registers for report tables
        topic_report, new = TopicStudentReport.objects.get_or_create(
            topic=block_topic,
            student=student,
        )
        topic_report.questions_answered += block_presentation.total
        topic_report.correct_question += block_presentation.hits
        topic_report.save()

        aok_report, new = AreaOfKnowledgeStudentReport.objects.get_or_create(
            area_of_knowledge=block_aok,
            student=student,
        )
        aok_report.questions_answered += block_presentation.total
        aok_report.correct_question += block_presentation.hits
        aok_report.save()

        while exp > student.level.points_required:
            exp -= student.level.points_required
            next_level = student.level.get_next_level()
            student.level = next_level

        student.points = Decimal(exp)
        student.save()

        account, new = CoinWallet.objects.get_or_create(student=student)

        block_transaction = BlockTransaction(
            blockPresentation=block_presentation,
            account=account,
        )
        block_transaction.save()
        student.import_new_topic_mastery()
        student.import_new_topic_status()
        student.update_student_topic_mastery(block_topic)
        student.update_student_topic_status(block_aok)

        block_presentation.delete()
        block_presentation.block.delete()

        return FinishBlockPresentation(
            block_presentation=block_presentation,
            student=student)


class Mutation(graphene.ObjectType):
    create_path_block_presentation = CreatePathBlockPresentation.Field()
    create_ai_block_presentation = CreateAIBlockPresentation.Field()
    finish_block_presentation = FinishBlockPresentation.Field()
    create_block_presentation_by_question_id = CreateBlockPresentationByQuestionId.Field()
    create_homework_block_presentation = CreateHomeworkBlockPresentation.Field()
