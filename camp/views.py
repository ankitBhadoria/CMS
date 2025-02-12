import datetime
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view,permission_classes,action
from rest_framework.permissions import BasePermission
# from rest_framework.views import APIView
from rest_framework import status
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

# from .tasks import create_message_task
from .serializers import UserProfileSerializer, UserSerializer,PracticeSerializer,CampaignSerializer,MessageSerializer,AdminCampaignSerializer,UserCampaignSequenceSerializer
from .models import UserProfile,Practice,Campaign,Message,AdminCampaign,UserCampaignSequence,engine
from sqlalchemy.orm import sessionmaker
from django.contrib.auth.models import User
from sqlalchemy.orm.exc import NoResultFound
from .utils import send_custom_email
from django.utils.timezone import make_aware
import logging

logger = logging.getLogger(__name__)

# from django.contrib.auth import authenticate, login, logout


Session = sessionmaker(bind=engine)
session = Session()

# @permission_classes([IsAuthenticated])
#  then in function
#  user = request.user

# class IsSuperAdmin(BasePermission):
#     """
#     Custom permission to allow only superadmin users to access the view.
#     """
#     def has_permission(self, request, view):
#         # Since user is already authenticated (checked by IsAuthenticated), 
#         # just check if the user is a superadmin
#         if request.user.role == 'superadmin':
#             return True
#         # If the user is not a superadmin
#         return False
    
# class IsAdmin(BasePermission):
#     """
#     Custom permission to allow only admin users to access the view.
#     """
#     def has_permission(self, request, view):
#         # Since user is already authenticated (checked by IsAuthenticated), 
#         # just check if the user is a admin
#         if request.user.role == 'admin':
#             return True
#         # If the user is not a admin
#         return False
    
# class IsPracticeUserAdmin(BasePermission):
#     """
#     Custom permission to allow only practiceuser users to access the view.
#     """
#     def has_permission(self, request, view):
#         # Since user is already authenticated (checked by IsAuthenticated), 
#         # just check if the user is a practiceuser
#         if request.user.role == 'practiceuser':
#             return True
#         # If the user is not a practiceuser
#         return False



# class UserProfileViewSet(viewsets.ViewSet):
#     from rest_framework.response import Response
# from rest_framework import status, viewsets
# from sqlalchemy.orm import sessionmaker
# from .models import UserProfile, engine
# from .serializers import UserProfileSerializer

# Session = sessionmaker(bind=engine)
# session = Session()


# for now unauthenticated so that user can be created
class UserProfileViewSet(viewsets.ViewSet):
    def list(self, request, *args, **kwargs):
        role = request.GET.get("role")
        practice_id = request.GET.get("practice_id")

        query = session.query(UserProfile)
        
        if role and practice_id:
            query = query.filter(UserProfile.role == role,UserProfile.practice_id == practice_id)

        user_profiles = query.all()
        serializer = UserProfileSerializer(user_profiles, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)


    def create(self, request, *args, **kwargs):
        user_data = request.data
    
        # Validate and create Django User
        user_serializer = UserSerializer(data=user_data)
        if user_serializer.is_valid():
            validated_data = user_serializer.validated_data

        # Create the user instance without saving to the database
            user = User(**validated_data)

        # Hash the password
            user.set_password(validated_data['password'])

        # Save the user instance to the database
            user.save()
        
        # Validate profile user data before creating UserProfile
            profile_user_data = (
                {'role': user_data['role'], 'id': user.id} 
                if user_data['role'] == 'superadmin' 
                else {'role': user_data['role'], 'id': user.id, 'practice_id': user_data.get('practice_id')}
            )

            user_profile_serializer = UserProfileSerializer(data=profile_user_data)
            if user_profile_serializer.is_valid():
                try:
                # Create UserProfile using SQLAlchemy
                    userpro = UserProfile(**profile_user_data)
                    session.add(userpro)
                    session.commit()
                
                    return Response({
                        "message": "User and its profile created successfully."
                    }, status=201)

                except Exception as e:
                    session.rollback()  # Rollback SQLAlchemy transaction if an error occurs
                    user.delete()  # Delete the Django user to maintain consistency
                    return Response({"message": f"Failed to create UserProfile: {str(e)}"}, status=400)

            else:
                user.delete()  # Delete the Django user if UserProfile validation fails
                return Response({"message": user_profile_serializer.errors}, status=400)

        else:
        # Extract the error messages
            errors = user_serializer.errors
            error_messages = [f"{key}: {value}" for key, value in errors.items()]
            error_message_str = ', '.join(error_messages)
            return Response({"message": error_message_str}, status=400)

    
    def retrieve(self, request, pk=None, *args, **kwargs):
        try:
        # Query the UserProfile using SQLAlchemy
            user_profile = session.query(UserProfile).filter_by(id=pk).first()
        
            if not user_profile:
                return Response({"message": "User profile not found."}, status=status.HTTP_404_NOT_FOUND)
        
        # Serialize the full user profile data
            serializer = UserProfileSerializer(user_profile)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
        # Handle unexpected errors
            return Response({"message": "An error occurred.", "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# for now unauthenticated because making practice manually from backend    
class PracticeViewSet(viewsets.ViewSet):
    def list(self, request, *args, **kwargs):
        # Use SQLAlchemy to query extended_user table
        users = session.query(Practice).all()
        serializer = PracticeSerializer(users, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = PracticeSerializer(data=request.data)
        if serializer.is_valid():
            try:
                practice_data = Practice(**serializer.validated_data)
                session.add(practice_data)
                session.commit()
                return Response({
                    "practice_id": practice_data.id,
                    "name": practice_data.name,
                    "message": "Practice created successfully."
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                session.rollback()
                return Response(f"Error: {e}", status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def retrieve(self, request, pk=None):
        try:
            practice = session.query(Practice).filter_by(id=pk).one()
            serializer = PracticeSerializer(practice)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except NoResultFound:
            return Response({"error": "Practice not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class CampaignViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    def list(self, request, *args, **kwargs):
        campaigns = session.query(Campaign).all()
        serializer = CampaignSerializer(campaigns, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = CampaignSerializer(data=request.data)
        if serializer.is_valid():
            try:
                campaign_data = Campaign(**serializer.validated_data)
                session.add(campaign_data)
                session.commit()
                return Response({
                    "campaign_id": campaign_data.id,
                    "name": campaign_data.type,
                    "description": campaign_data.description,
                    "message": "Campaign created successfully."
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                session.rollback()
                return Response(f"Error: {e}", status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None, *args, **kwargs):
        try:
            campaign = session.query(Campaign).filter(Campaign.id == pk).first()
            if not campaign:
                return Response({"message": "Campaign not found."}, status=status.HTTP_404_NOT_FOUND)
            serializer = CampaignSerializer(campaign)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(f"Error: {e}", status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None, *args, **kwargs):
        serializer = CampaignSerializer(data=request.data, partial=True)
        if serializer.is_valid():
            try:
                campaign = session.query(Campaign).filter(Campaign.id == pk).first()
                if not campaign:
                    return Response({"message": "Campaign not found."}, status=status.HTTP_404_NOT_FOUND)
                
                for key, value in serializer.validated_data.items():
                    setattr(campaign, key, value)
                
                session.commit()
                return Response({
                    "campaign_id": campaign.id,
                    "name": campaign.type,
                    "description": campaign.description,
                    "message": "Campaign updated successfully."
                }, status=status.HTTP_200_OK)
            except Exception as e:
                session.rollback()
                return Response(f"Error: {e}", status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None, *args, **kwargs):
        try:
            campaign = session.query(Campaign).filter(Campaign.id == pk).first()
            if not campaign:
                return Response({"message": "Campaign not found."}, status=status.HTTP_404_NOT_FOUND)

            session.delete(campaign)
            session.commit()
            return Response({"message": "Campaign deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            session.rollback()
            return Response(f"Error: {e}", status=status.HTTP_400_BAD_REQUEST)
        
class AdminCampaignViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    """
    A viewset for viewing and managing AdminCampaign instances.
    """

    def list(self, request, *args, **kwargs):
        practice_id = request.query_params.get("practice_id")
        print(practice_id)
        admin_campaigns = session.query(AdminCampaign)
        if practice_id:
            admin_campaigns = admin_campaigns.filter(AdminCampaign.belongto == practice_id)
        admin_campaigns = admin_campaigns.all()
        serializer = AdminCampaignSerializer(admin_campaigns, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = AdminCampaignSerializer(data=request.data)
        if serializer.is_valid():
            try:
                admin_campaign_data = AdminCampaign(**serializer.validated_data)
                session.add(admin_campaign_data)
                session.commit()
                return Response({
                    "admin_campaign_id": admin_campaign_data.id,
                    "name": admin_campaign_data.type,
                    "description": admin_campaign_data.description,
                    "message": "Admin campaign created successfully."
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                session.rollback()
                return Response(f"Error: {e}", status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None, *args, **kwargs):
        try:
            admin_campaign = session.query(AdminCampaign).filter(AdminCampaign.id == pk).first()
            if not admin_campaign:
                return Response({"message": "Admin campaign not found."}, status=status.HTTP_404_NOT_FOUND)
            serializer = AdminCampaignSerializer(admin_campaign)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(f"Error: {e}", status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None, *args, **kwargs):
        serializer = AdminCampaignSerializer(data=request.data, partial=True)
        if serializer.is_valid():
            try:
                admin_campaign = session.query(AdminCampaign).filter(AdminCampaign.id == pk).first()
                if not admin_campaign:
                    return Response({"message": "Admin campaign not found."}, status=status.HTTP_404_NOT_FOUND)
                
                for key, value in serializer.validated_data.items():
                    setattr(admin_campaign, key, value)
                
                session.commit()
                return Response({
                    "admin_campaign_id": admin_campaign.id,
                    "name": admin_campaign.type,
                    "description": admin_campaign.description,
                    "message": "Admin campaign updated successfully."
                }, status=status.HTTP_200_OK)
            except Exception as e:
                session.rollback()
                return Response(f"Error: {e}", status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None, *args, **kwargs):
        try:
            admin_campaign = session.query(AdminCampaign).filter(AdminCampaign.id == pk).first()
            if not admin_campaign:
                return Response({"message": "Admin campaign not found."}, status=status.HTTP_404_NOT_FOUND)

            session.delete(admin_campaign)
            session.commit()
            return Response({"message": "Admin campaign deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            session.rollback()
            return Response(f"Error: {e}", status=status.HTTP_400_BAD_REQUEST)


class MessageViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    """
    A viewset for viewing and editing Message instances.
    """

    def list(self, request, *args, **kwargs):
        try:
            # Filter messages by userprofile_id
            messages = session.query(Message).filter(Message.userprofile_id == request.user.id).all()

            serializer = MessageSerializer(messages, many=True)
            return Response(serializer.data)

        except Exception as e:
            return Response({"message": "An error occurred.", "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request, *args, **kwargs):
        serializer = MessageSerializer(data=request.data)

        if serializer.is_valid():
            validated_data = serializer.validated_data
            userprofile_id = validated_data.get("userprofile_id")
            user = User.objects.filter(id=userprofile_id).first()
            if not user or not user.email:
                return Response({"error": "User email not found"}, status=status.HTTP_400_BAD_REQUEST)

            recipient_email = [user.email]  # Convert to list for sending mail

            try:
                message = Message(**validated_data)
                session.add(message)
                session.commit()
                # Send email
                subject = "New Campaign Notification"
                # Extract only required fields
                name = validated_data.get("name", "N/A")
                campaign_type = validated_data.get("type", "N/A")
                description = validated_data.get("description", "N/A")
                status_value = validated_data.get("status", "N/A")

                # Format email content
                email_body = (
                    f"New Campaign Notification\n\n"
                    f"Name: {name}\n"
                    f"Type: {campaign_type}\n"
                    f"Description: {description}\n"
                    f"Status: {status_value}"
                )
                send_custom_email(subject, email_body, recipient_email)
                
                return Response({"message": "Message created and email sent successfully!"}, status=status.HTTP_201_CREATED)
            except Exception as e:
                session.rollback()
                return Response(f"Error: {e}", status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # @action(detail=False, methods=["post"], url_path="instant")
    # def create_instant(self, request, *args, **kwargs):
    #     """Instantly creates a message and sends an email."""
    #     serializer = MessageSerializer(data=request.data)

    #     if serializer.is_valid():
    #         # print(serializer.validated_data)
    #         validated_data = serializer.validated_data
    #         session = Session()

    #         try:
    #             userprofile_id = validated_data.get("userprofile_id")
    #             user = session.query(User).filter_by(id=userprofile_id).first()

    #             if not user or not user.email:
    #                 return Response({"error": "User email not found"}, status=status.HTTP_400_BAD_REQUEST)

    #             recipient_email = [user.email]  

    #             # Create message instantly
    #             message = Message(**validated_data)
    #             session.add(message)
    #             session.commit()

    #             # Send email
    #             from django.core.mail import send_mail
    #             from django.conf import settings

    #             subject = "New Campaign Notification"
    #             email_body = (
    #                 f"New Campaign Notification\n\n"
    #                 f"Name: {validated_data.get('name', 'N/A')}\n"
    #                 f"Type: {validated_data.get('type', 'N/A')}\n"
    #                 f"Description: {validated_data.get('description', 'N/A')}\n"
    #                 f"Status: {validated_data.get('status', 'N/A')}"
    #             )

    #             send_mail(
    #                 subject,
    #                 email_body,
    #                 settings.DEFAULT_FROM_EMAIL,
    #                 recipient_email,
    #                 fail_silently=False,
    #             )
        

    #             return Response({"message": "Message created and email sent successfully!"}, status=status.HTTP_201_CREATED)

    #         except Exception as e:
    #             session.rollback()
    #             return Response(f"Error: {e}", status=status.HTTP_400_BAD_REQUEST)

    #         finally:
    #             session.close()

    #     else:
    #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # @action(detail=False, methods=["post"], url_path="schedule")
    # def create_scheduled(self, request, *args, **kwargs):
    #     """Schedules message creation and email sending at user-specified time."""
    #     # print(request.data)
    #     serializer = MessageSerializer(data=request.data)

    #     if serializer.is_valid():
    #         validated_data = serializer.validated_data
    #         scheduled_time = request.data.get("scheduled_time")

    #         if not scheduled_time:
    #             return Response({"error": "Scheduled time is required"}, status=status.HTTP_400_BAD_REQUEST)

    #         # Convert scheduled_time to timezone-aware datetime
    #         scheduled_time = make_aware(scheduled_time)

    #         # Ensure the scheduled time is in the future
    #         if scheduled_time <= datetime.now():
    #             return Response({"error": "Scheduled time must be in the future"}, status=status.HTTP_400_BAD_REQUEST)

    #         # Schedule the task at user-defined time
    #         create_message_task.apply_async(
    #             args=[validated_data],
    #             eta=scheduled_time  
    #         )
    #         # print(serializer.validated_data)

    #         return Response(
    #             {"message": f"Message scheduled successfully for {scheduled_time}"},
    #             status=status.HTTP_202_ACCEPTED
    #         )
    #     else:
    #         print('validation failed')
    #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None, *args, **kwargs):
        """
        Update a message instance. Supports partial updates.
        """
        try:
            message = session.query(Message).filter(Message.id == pk).first()
            if not message:
                return Response({"error": "Message not found."}, status=status.HTTP_404_NOT_FOUND)

            serializer = MessageSerializer(message, data=request.data, partial=True)

            if serializer.is_valid():
                for key, value in serializer.validated_data.items():
                    setattr(message, key, value)

                session.commit()
                return Response({
                    "message": "Message updated successfully!",
                    "updated_message": serializer.data
                }, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            session.rollback()
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, pk=None, *args, **kwargs):
        try:
            message = session.query(Message).filter(Message.id == pk).first()
            if not message:
                return Response({"error": "Message not found."}, status=status.HTTP_404_NOT_FOUND)

            session.delete(message)
            session.commit()
            return Response({"message": "Message deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

        except Exception as e:
            session.rollback()
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
# class UserCampaignSequenceViewSet(viewsets.ViewSet):
#     permission_classes = [IsAuthenticated]
#     """ViewSet for creating UserCampaignSequence records"""

#     def create(self, request):
#         """Handles the creation of a UserCampaignSequence."""
#         logger.info("Received request to create UserCampaignSequence: %s", request.data)
#         request.data["created_by"]=request.user.id
#         serializer = UserCampaignSequenceSerializer(data=request.data)
#         serializer.is_valid()
#         # for k,v in serializer:
#         #     logger.info(f"key is {k} and value is {v}")
#         logger.info(f"serializer {serializer}")
#         if serializer.is_valid():
#             # logger.info(f"the schedule status is {serializer["schedule_status"]}")
#             validated_data = serializer.validated_data
#             logger.debug("Validated data: %s", validated_data)

#             try:
#                 # Create a new UserCampaignSequence instance
#                 logger.info("going in the fucntion.")
#                 validated_data["schedule_status"]="scheduled"
#                 new_sequence = UserCampaignSequence(**validated_data)
#                 session.add(new_sequence)
#                 session.commit()
#                 logger.info("UserCampaignSequence created successfully: ID %s", new_sequence.id)
#                 return Response({"message": "UserCampaignSequence created successfully!"}, status=status.HTTP_201_CREATED)
#             except Exception as e:
#                 session.rollback()  # Rollback in case of an error
#                 logger.error("Error creating UserCampaignSequence: %s", str(e), exc_info=True)
#                 return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
#             finally:
#                 session.close()  # Close session
#                 logger.debug("Database session closed.")
#         print('serializer caused error')
#         logger.warning("Invalid data received: %s", serializer.errors)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserCampaignSequenceViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    """ViewSet for creating UserCampaignSequence records"""

    def create(self, request):
        """Handles the creation of a UserCampaignSequence."""
        request.data["created_by"] = request.user.id
        serializer = UserCampaignSequenceSerializer(data=request.data)
        
        if serializer.is_valid():
            validated_data = serializer.validated_data

            try:
                # Create a new UserCampaignSequence instance
                validated_data["schedule_status"] = "scheduled"
                session.rollback() 
                sequence = UserCampaignSequence(**validated_data)
                session.add(sequence)
            
                session.flush()  # Try flushing before committing

                session.commit()
                return Response({"message": "UserCampaignSequence created successfully!"}, status=status.HTTP_201_CREATED)
            except Exception as e:
                session.rollback()  # Rollback in case of an error
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            # finally:
            #     session.close()  # Close session
        else:
            print('serizlizer not working')
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

