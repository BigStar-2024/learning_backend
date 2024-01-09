from django.conf import settings
from django.shortcuts import render, redirect
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from django.contrib.auth.forms import PasswordResetForm
from games.models import PlayGameTransaction
from payments.models import PaymentHistory
from users.models import User
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from app.settings.env import IS_PRODUCTION, DOMAIN_WITHOU_PRTC
from datetime import timedelta
from django.utils import timezone
from django.db.models import Count
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.http import HttpResponse, HttpResponseRedirect
def password_reset_request(request):
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            associated_users = User.objects.filter(Q(email=data))
            if associated_users.exists():
                for user in associated_users:
                    subject = "Password Reset Requested"
                    email_template_name = "emails/password/password_reset_email.txt"
                    c = {
                        "email": user.email,
                        'domain': DOMAIN_WITHOU_PRTC,
                        'site_name': 'Website',
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "user": user,
                        'token': default_token_generator.make_token(user),
                        'protocol': 'http',
                    }
                    email = render_to_string(email_template_name, c)
                    try:
                        send_mail(subject, email, 'Learn With Socrates',
                                  [user.email], fail_silently=False)
                    except BadHeaderError:
                        return HttpResponse('Invalid header found.')
                    return redirect("/password_reset/done/")
    password_reset_form = PasswordResetForm()
    return render(request=request, template_name="emails/password/password_reset.html", context={"password_reset_form": password_reset_form})
