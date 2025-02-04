# from rest_framework import viewsets
# from rest_framework.response import Response
# from rest_framework import status
from rest_framework.permissions import BasePermission
# from django.core.mail import send_mail
# from django.contrib.auth.models import User as DjangoUser
# from .serializers import EmailSerializer
# from .models import UserCampaign, UserMessage
# from .serializers import UserCampaignSerializer
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy import create_engine
# from extended_user.models import extended_user
# import logging

# Create a logger for this file
# logger = logging.getLogger(_name_)

# DATABASE_URL = "postgresql://postgres:Anjul123@localhost:5432/lightbulb"
# engine = create_engine(DATABASE_URL)
# Session = sessionmaker(bind=engine)
# session = Session()
    
def check_if_superadmin(user_id):
    """
    Checks if a given user ID exists in the database and if their role is 'superadmin'.
    Returns True if user exists and is a superadmin, otherwise False.
    """
    logger.info(f"Checking superadmin status for user_id: {user_id}")
    try:
        user = session.query(extended_user).filter_by(id=user_id).first()
        
        if user and user.role == 'superadmin':
            logger.info(f"User {user_id} confirmed as superadmin")
            return True
        logger.warning(f"User {user_id} is not a superadmin or doesn't exist")
        return False
        
    except Exception as e:
        logger.error(f"Error checking superadmin status for user {user_id}: {str(e)}", exc_info=True)
        return False
    finally:
        session.close()

def check_if_admin(user_id):
    """
    Checks if a given user ID exists in the database and if their role is 'admin'.
    Returns True if user exists and is a admin, otherwise False.
    """
    logger.info(f"Checking admin status for user_id: {user_id}")
    try:
        user = session.query(extended_user).filter_by(id=user_id).first()
        
        if user and user.role == 'admin':
            logger.info(f"User {user_id} confirmed as admin")
            return True
        logger.warning(f"User {user_id} is not a admin or doesn't exist")
        return False
        
    except Exception as e:
        logger.error(f"Error checking admin status for user {user_id}: {str(e)}", exc_info=True)
        return False
    finally:
        session.close()

class IsSuperAdmin(BasePermission):
    """
    Custom permission to allow only superadmin users to access the view.
    """
    def has_permission(self, request, view):
        # Since user is already authenticated (checked by IsAuthenticated), 
        # just check if the user is a superadmin
        if check_if_superadmin(request.user.id):
            return True
        # If the user is not a superadmin
        return False

class IsAdmin(BasePermission):
    """
    Custom permission to allow only admin users to access the view.
    """
    def has_permission(self, request, view):
        # Since user is already authenticated (checked by IsAuthenticated), 
        # just check if the user is a admin
        if check_if_admin(request.user.id):
            return True

        # If the user is not a admin
        return False
# class SendTestEmailViewSet(viewsets.ViewSet):
#     """
#     A simple ViewSet for sending test emails.
#     """
#     permission_classes=[IsAuthenticated, IsAdmin]
#     def create(self, request):
#         logger.info("Received request to send test email")
#         serializer = EmailSerializer(data=request.data)
#         if serializer.is_valid():
#             if serializer.validated_data['on_email']:
#                 campaign = session.query(UserCampaign).filter(UserCampaign.id==serializer.validated_data['campaign_id'], UserCampaign.status=="pending").first()    
#                 subject, message ="",""
#                 logger.info(f"campaign object that we got: {campaign}")
#                 if campaign:
#                     subject = campaign.text
#                     message = campaign.description
#                 try:
#                     logger.debug("Querying users with 'user' role")
#                     users_with_role = session.query(extended_user).filter(extended_user.role=='user')
#                     user_ids = [user.id for user in users_with_role]
#                     users_list = DjangoUser.objects.filter(id__in=user_ids).values_list('email', flat=True)
#                     total_users = len(users_list)
                    
#                     logger.info(f"Attempting to send email to {total_users} users")
#                     logger.info(f"Recipient list is {users_list}")
#                     send_mail(subject=subject, message=message,from_email="anjulkushwaha11@gmail.com", recipient_list=users_list)
#                     logger.info("Email sent successfully")
                    
#                     return Response({"message": "Email sent successfully!", "Total users":total_users}, 
#                                 status=status.HTTP_201_CREATED)
#                 except Exception as e:
#                     logger.error(f"Failed to send email: {str(e)}", exc_info=True)
#                     return Response({"error": "Failed to send email"}, 
#                                 status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#             else:
#                 campaign = session.query(UserCampaign).filter(UserCampaign.id==serializer.validated_data['campaign_id']).first()    
#                 logger.info(f"campaign object that we got: {campaign}")
#                 if not campaign:
#                     logger.error(f"No campaign with this id")
#                     return
#                 try:
#                     logger.debug("Querying users with 'user' role")
#                     users_with_role = session.query(extended_user).filter(extended_user.role=='user')
#                     user_ids = [user.id for user in users_with_role]
#                     total_users = len(user_ids)
#                     logger.info(f"Attempting to send message to {total_users} users")
#                     logger.info(f"Recipient list is {user_ids}")
#                     for user in user_ids:
#                         existing_record = (
#                             session.query(UserMessage)
#                             .filter_by(user_id=user, campaign_id=campaign.id)
#                             .first()
#                         )
#                         if not existing_record:
#                             new_record = UserMessage(user_id=user,campaign_id=campaign.id)
#                             session.add(new_record)
#                             session.commit()
                        
                    
                    
#                     logger.info("message sent successfully")
                    
#                     return Response({"message": "message sent successfully!", "Total users":total_users}, 
#                                 status=status.HTTP_201_CREATED)
#                 except Exception as e:
#                     logger.error(f"Failed to send message: {str(e)}", exc_info=True)
#                     return Response({"error": "Failed to send message"}, 
#                                 status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
            
#         logger.warning(f"Invalid data provided: {serializer.errors}")
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def list(self, request, *args, **kwargs):
#         logger.info("Received request to list all user campaigns")
#         try:
#             campaigns = session.query(UserCampaign).all()
#             campaign_count = len(campaigns)
#             logger.info(f"Successfully retrieved {campaign_count} campaigns")
            
#             serializer = UserCampaignSerializer(campaigns, many=True)
#             return Response(serializer.data)
#         except Exception as e:
#             logger.error(f"Failed to retrieve campaigns: {str(e)}", exc_info=True)
#             return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
#         finally:
#             session.close()
# class UserCampaignViewSet(viewsets.ViewSet):
#     """
#     A viewset for viewing and creating user campaigns using SQLAlchemy.
#     """
#     permission_classes = [IsAuthenticated, IsSuperAdmin]
#     def create(self, request, *args, **kwargs):
#         logger.info("Received request to create new user campaign")
#         logger.debug(f"Request data: {request.data}")
#         created_by = request.user.id
#         request.data['created_by']=created_by
#         serializer = UserCampaignSerializer(data=request.data)
#         if not serializer.is_valid():
#             logger.warning(f"Invalid campaign data provided: {serializer.errors}")
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         try:
#                 logger.debug(f"serializer: {serializer}")
#                 user_campaign_data = serializer.validated_data
#                 logger.debug(f"Data from serializer: {serializer.validated_data}")
#                 logger.debug(f"Creating new campaign with data: {user_campaign_data}")
                
#                 new_campaign = UserCampaign(
#                     type=user_campaign_data['type'],
#                     text=user_campaign_data['text'],
#                     description=user_campaign_data.get('description', ''),
#                     created_by=user_campaign_data['created_by'],
#                     status=user_campaign_data['status'],
#                 )
#                 session.add(new_campaign)
#                 session.commit()
#                 logger.info(f"Successfully created new campaign by user {created_by}")
                
#                 response_serializer = UserCampaignSerializer(new_campaign)
#                 return Response(response_serializer.data, status=status.HTTP_201_CREATED)

#         except Exception as e:
#             session.rollback()
#             logger.error(f"Failed to create campaign: {str(e)}", exc_info=True)
#             return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
#         finally:
#             session.close()
#     def list(self, request, *args, **kwargs):
#         logger.info("Received request to list all user campaigns")
#         try:
#             campaigns = session.query(UserCampaign).all()
#             campaign_count = len(campaigns)
#             logger.info(f"Successfully retrieved {campaign_count} campaigns")
            
#             serializer = UserCampaignSerializer(campaigns, many=True)
#             return Response(serializer.data)
#         except Exception as e:
#             logger.error(f"Failed to retrieve campaigns: {str(e)}", exc_info=True)
#             return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
#         finally:
#             session.close()
#     def retrieve(self,request,pk=None, *args, **kwargs):
#         try:
#             campaign = session.query(UserCampaign).filter(UserCampaign.id==pk).first()
#             if campaign is None:
#                 return Response({"detail": "Campaign not found"}, status=status.HTTP_404_NOT_FOUND)
#             serializer = UserCampaignSerializer(campaign)
#             return Response(serializer.data)
#         except Exception as e:
#             logger.error(f"Failed to retrieve campaign by ID {pk}: {str(e)}", exc_info=True)
#             return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
#         finally:
#             session.close()

#     def update(self,request,pk=None, args,*kwargs):
#         try:
#             campaign = session.query(UserCampaign).filter(UserCampaign.id==pk).first()
#             if campaign is None:
#                 return Response({"detail": "Campaign not found"}, status=status.HTTP_404_NOT_FOUND)
#             request.data["created_by"]=request.user.id
#             serializer = UserCampaignSerializer(data=request.data)
#             if not serializer.is_valid():
#                 logger.warning(f"Invalid campaign update data: {serializer.errors}")
#                 return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#             campaign.type = request.data.get('type', campaign.type)
#             campaign.text = request.data.get('text', campaign.text)
#             campaign.description = request.data.get('description', campaign.description)
#             campaign.status = request.data.get('status', campaign.status)
#             campaign.created_by = request.user.id or campaign.created_by
#             # Commit the changes to the database
#             session.commit()

#             # Serialize the updated campaign and return the response
#             response_serializer = UserCampaignSerializer(campaign)
#             return Response(response_serializer.data, status=status.HTTP_200_OK)
#         except Exception as e:
#             session.rollback()
#             logger.error(f"Failed to update campaign {pk}: {str(e)}", exc_info=True)
#             return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
#         finally:
#             session.close()
                
# # class MessageViewSet()
