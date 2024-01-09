from django.db.models import Count, F
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from django.core.mail import send_mail
from guardians.models import GuardianStudent
from organization.models.schools import SchoolTeacher
from block.models import BlockQuestionPresentation
from games.models import PlayGameTransaction
from payments.models import PaymentHistory
from users.models import User
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from datetime import timedelta
from django.utils import timezone
from django.utils.html import strip_tags
from datetime import datetime, timedelta
from app.services import encrypt

def send_report_mail(send=True, prevDay = 0):
    end_date = timezone.now() - timedelta(days=+prevDay)
    start_date = end_date - timedelta(days=2)
    print("===========Starting Send Report Email / "+end_date.strftime("%Y/%m/%d, %H:%M:%S")+"=============" )
    email_title = "Report"
    email_template_name = "emails/report/index.html"
    email_receivers = settings.REPORT_EMAIL_RECEIVERS
    project_name = "Prod Server" if settings.IS_PRODUCTION else "Dev Server"

    userHistory = (User.objects
        .filter((Q(create_timestamp__gt = start_date) & Q(create_timestamp__lte = end_date)) | (Q(last_login__gt = start_date) & Q(last_login__lte = end_date)))
        .annotate(num_correct_questions=Count('student__studentblockquestionpresentationhistory__block_question_presentation__id', distinct=True, filter=(Q(student__user__id=F("id")) & Q(student__studentblockquestionpresentationhistory__block_question_presentation__status=BlockQuestionPresentation.STATUS_CORRECT) & Q(student__studentblockquestionpresentationhistory__block_question_presentation__status=BlockQuestionPresentation.STATUS_CORRECT) & Q(student__studentblockquestionpresentationhistory__block_question_presentation__update_timestamp__gt=start_date) & Q(student__studentblockquestionpresentationhistory__block_question_presentation__update_timestamp__lte=end_date))))
        .annotate(num_wrong_questions=Count('student__studentblockquestionpresentationhistory__block_question_presentation__id', distinct=True, filter=(Q(student__user__id=F("id")) & Q(student__studentblockquestionpresentationhistory__block_question_presentation__status=BlockQuestionPresentation.STATUS_INCORRECT) & Q(student__studentblockquestionpresentationhistory__block_question_presentation__update_timestamp__gt=start_date) & Q(student__studentblockquestionpresentationhistory__block_question_presentation__update_timestamp__lte=end_date))))
        .annotate(num_purchased_collectibles=Count('student__studentcollectible__id', distinct=True, filter=Q(student__user__id=F("id")) & Q(student__studentcollectible__update_timestamp__gt=start_date) & Q(student__studentcollectible__update_timestamp__lte=end_date)))
        .all()
    )
    for user in userHistory:

        coupon_code = None
        if user.profile.role == 'guardian':
            coupon_code = user.guardian.coupon_code if hasattr(user, 'guardian') else None
        elif user.profile.role == 'teacher':
            school_personnel = user.schoolpersonnel

            # if the teacher is connected to SchoolTeacher, this is school teacher, else individual teacher
            try:
                school_teacher = SchoolTeacher.objects.get(teacher=school_personnel.teacher)
                coupon_code = school_teacher.school.schoolsubscriber.subscriber.coupon_code
            except SchoolTeacher.DoesNotExist:
                # if this is individual teacher, he will have coupon code info if he joined with coupon code
                coupon_code = school_personnel.coupon_code
            except Exception:
                print(Exception)
        elif user.profile.role == 'student':
            # There are 2 kinds of student: guardian student or classroom student
            try:
                # for the guardian student
                guardian_student = GuardianStudent.objects.get(student=user.student)
                coupon_code = guardian_student.guardian.coupon_code if hasattr(guardian_student, 'guardian') else None

            except GuardianStudent.DoesNotExist:
                # This is classroom student
                # if this student is of individual teacher, will have coupon code.
                teacher = user.student.classroom.teacherclassroom.teacher
                coupon_code = teacher.coupon_code

                # if this is not individual teacher or individual teacher with no coupon
                if coupon_code is None and hasattr(teacher, 'schoolteacher'):
                    # The school teacher
                    coupon_code = teacher.schoolteacher.school.schoolsubscriber.subscriber.coupon_code
            except Exception:
                print(Exception)
        elif user.profile.role == 'adminTeacher':
            admin_person = user.schoolpersonnel.administrativepersonnel if hasattr(user.schoolpersonnel, 'administrativepersonnel') else None
            coupon_code = admin_person.schooladministrativepersonnel.school.schoolsubscriber.subscriber.coupon_code
            # print('Admin: ', school_admin_personnel)
        elif user.profile.role == 'subscriber':
            coupon_code = user.schoolpersonnel.coupon_code
        else:
            pass
        
        user.discount_code = coupon_code.code if hasattr(coupon_code, 'code') else '-' 

        try:
            coin_wallet = user.student.coinWallet
            game_transactions = PlayGameTransaction.objects.filter(account = coin_wallet, update_timestamp__gt = start_date, update_timestamp__lte = end_date)
            game_transactions_count = game_transactions.count()
            user.num_played_games = game_transactions_count
        except Exception as e:
            user.num_played_games = 0

    num_creat_today = userHistory.filter(last_login__gt = start_date).filter(create_timestamp__lte = end_date).count()
    num_login_today = userHistory.filter(create_timestamp__gt = start_date).filter(last_login__lte = end_date).count()
    #-------------------- Get Payment History -S---------------------#
    paymentHistory = PaymentHistory.objects.filter(update_timestamp__gt = start_date, update_timestamp__lte = end_date).filter(Q(type="payment_action_intent_succeeded") | Q(type="payment_action_intent_failed")).all()
    #-------------------- Get Payment History -E---------------------#
    
    #-------------------- Get Universal Password -S-------------------#
    now = datetime.now()
    format = "%Y-%m-%d %H:%M:%S"
    universal_password = encrypt(datetime.strftime((now),format))
    #-------------------- Get Universal Password -E-------------------#

    email = render_to_string(email_template_name, {"project_name": project_name, "num_creat_today": num_creat_today, "num_login_today": num_login_today,"today": end_date, "yesterday": start_date, "userHistories": userHistory, "paymentHistories": paymentHistory, "universal_password": universal_password})
    email_content = strip_tags(email)

    if(send == True):
        try:
            send_mail(email_title, email_content, 'Learn With Socrates',
                        email_receivers, fail_silently=False, html_message=email)
        except Exception as e:
            print(e)

    print("===========Finishing Send Report Email / "+timezone.now().strftime("%Y/%m/%d, %H:%M:%S")+"=============" )
    return {"email":email, "universal_password": universal_password, "num_creat_today": num_creat_today, "num_login_today": num_login_today,"today": end_date, "yesterday": start_date, "userHistories": userHistory, "paymentHistories": paymentHistory, "success": True, "message": [{"message":"Report Email has been successfully sent!"}],}