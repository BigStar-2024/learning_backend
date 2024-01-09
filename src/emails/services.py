from logging import exception
from unicodedata import name
from django.conf import settings
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.core.mail import send_mail
from .models import EmailTemplate, EmailHistory
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def sendTemplate(
        to_emails,
        template_id,
        data_keys,
        data_values,
        from_email=settings.SENDGRID_DEFAULT_SENDER):

    message = Mail(
        from_email=from_email,
        to_emails=to_emails,
    )

    template_data = {}

    for key, value in zip(data_keys, data_values):
        template_data[key] = value

    message.template_id = template_id
    message.dynamic_template_data = template_data

    try:
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = sg.send(message)
        code, body, headers = response.status_code, response.body, response.headers
        print(f"Response code: {code}")
        print(f"Response headers: {headers}")
        print(f"Response body: {body}")
        print("Dynamic Messages Sent!")
    except Exception as e:
        return str("Error: {0}".format(e))
    return str(response.status_code)


def sendSignUpEmail(
    template_name,  # guardian, teacher, subscriber
    to_email,
    customer,  # user reference
):
    try:
        print('Sending signup email for ', template_name)
        emailTemplate = EmailTemplate.objects.get(name=template_name)
        realContent = emailTemplate.content.replace(
            "{{customer_name}}", customer.first_name)
        send_mail(
            'Welcome to Learn With Socrates!',
            strip_tags(realContent),
            'Learn With Scorates',
            [to_email],
            fail_silently=False,
            html_message='<html><body>' + realContent + '</body></html>'
        )

        emailHistory = EmailHistory(
            email_template=emailTemplate, user=customer, success=True)
        emailHistory.save()
        print('Finished sending sign up email')
    except (Exception) as e:
        print('Sending email failed. \nError code:', e)
        emailHistory = EmailHistory(user=customer, success=False, note=e)
        emailHistory.save()
