from django.core.mail import send_mail
from django.conf import settings

def send_custom_email(subject, message, recipient_list, from_email=None):
    """ Sends an email using Django's send_mail function """
    if from_email is None:
        from_email = settings.EMAIL_HOST_USER  # Set default sender email
    send_mail(subject, message, from_email, recipient_list)
