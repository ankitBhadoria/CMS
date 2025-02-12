from __future__ import absolute_import, unicode_literals
from datetime import datetime  
from celery import shared_task
from sqlalchemy.orm import sessionmaker
from django.core.mail import send_mail
from django.conf import settings

import django
django.setup()

from .utils import send_custom_email
from .models import UserCampaignSequence, Message, engine
from django.contrib.auth.models import User

Session = sessionmaker(bind=engine)
session = Session()

@shared_task
def create_scheduled_messages():
    """Checks the database for scheduled messages and processes them."""
    
    # Find scheduled messages that need to be sent
    scheduled_messages = session.query(UserCampaignSequence).filter(
        UserCampaignSequence.schedule_status == "scheduled",
        UserCampaignSequence.scheduled_date <= datetime.now()
    ).all()

    for message in scheduled_messages:
        # Fetch user from SQLAlchemy model (not Django)
        user = User.objects.filter(id=message.userprofile_id).first()
        
        if user and user.email:
            recipient_email = [user.email]

            # ✅ Correct attribute access (no `.get()`)
            type_ = message.type  
            name = message.name  
            description = message.description  
            status = message.status  
            userprofile_id = message.userprofile_id  

            # ✅ Correct Message instance creation
            message_instance = Message(
                type=type_,
                name=name,
                description=description,
                status=status,
                userprofile_id=userprofile_id
            )
                
            session.add(message_instance)
            session.commit()

            # ✅ Send email
            subject = "New Campaign Notification"
            email_body = (
                f"New Campaign Notification\n\n"
                f"Name: {name}\n"
                f"Type: {type_}\n"
                f"Description: {description}\n"
                f"Status: {status}"
            )
            send_custom_email(subject, email_body, recipient_email)

            # ✅ Update the message status
            message.schedule_status = "sent"
            session.commit()

    session.close()
