from django.core.mail import send_mail
from django.conf import settings
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from .services import sendTemplate
import graphene


# Send mail with django-mailer
class SendMail(graphene.Mutation):
    email = graphene.String()

    class Arguments:
        email = graphene.String(required=True)

    def mutate(self, info, email):
        send_mail(
            'Subject',
            'Message.',
            settings.SENDGRID_DEFAULT_SENDER,
            [email],
            fail_silently=False,
        )

        return SendMail(email=email)


class SendMailSendgrid(graphene.Mutation):
    email = graphene.String()
    message = graphene.String()

    class Arguments:
        email = graphene.String(required=True)

    def mutate(self, info, email):
        message = Mail(
            from_email=settings.SENDGRID_DEFAULT_SENDER,
            to_emails=[email],
            subject='Subject',
            plain_text_content='Message.',
        )
        try:
            sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
            sg.send(message)
        except Exception as e:
            return str(e)

        return SendMailSendgrid(email=email, message=message)


class SendTemplateSendgrid(graphene.Mutation):
    status = graphene.String()

    class Arguments:
        to_emails = graphene.List(graphene.String, required=True)
        template_id = graphene.String(required=True)
        data_keys = graphene.List(graphene.String, required=True)
        data_values = graphene.List(graphene.String, required=True)

    def mutate(
            self,
            info,
            to_emails,
            template_id,
            data_keys,
            data_values,
            ):

        status = sendTemplate(
            to_emails,
            template_id,
            data_keys,
            data_values,
            )

        return SendTemplateSendgrid(status=status)


class Mutation(graphene.ObjectType):
    send_mail = SendMail.Field()
    send_mail_sendgrid = SendMailSendgrid.Field()
    send_template_sendgrid = SendTemplateSendgrid.Field()
