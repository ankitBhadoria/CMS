# serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Campaign,UserProfile,Practice,Message,engine
from sqlalchemy.orm import sessionmaker
# serializers.py

Session = sessionmaker(bind=engine)
session = Session()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}
        
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value
        

# Custom serializer for SQLAlchemy model

class UserProfileSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    practice_id = serializers.IntegerField(required=False)
    role = serializers.ChoiceField(
        choices=["superadmin", "admin","practiceuser"]
    )
    
    def validate_practice_id(self, value):
        if value and not session.query(Practice).filter_by(id=value).first():
            raise serializers.ValidationError("The specified practice does not exist.")
        return value
        
class PracticeSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=50)
    is_active = serializers.BooleanField(required=False)
    created_by = serializers.IntegerField()
    
    def validate_created_by(self, value):
        if not session.query(UserProfile).filter_by(id=value).first():
            raise serializers.ValidationError("The specified user does not exist.")
        return value


class CampaignSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=50)
    type = serializers.CharField(max_length=50)
    description = serializers.CharField()
    status = serializers.ChoiceField(
        choices=["upcoming", "running", "expired"]
    )
    
class AdminCampaignSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=50)
    type = serializers.CharField(max_length=50)
    description = serializers.CharField()
    status = serializers.ChoiceField(
        choices=["upcoming", "running", "expired"]
    )
    belongto = serializers.IntegerField()
    
    def validate_practice_id(self, value):
        if value and not session.query(Practice).filter_by(id=value).first():
            raise serializers.ValidationError("The specified practice does not exist.")
        return value
    
class MessageSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    type = serializers.CharField(max_length=50)
    name = serializers.CharField(max_length=50)
    description = serializers.CharField()
    status = serializers.ChoiceField(choices=["upcoming", "running", "expired"])
    userprofile_id = serializers.IntegerField()
    seen = serializers.ChoiceField(choices=["yes", "no"], default="no")  # New field

    def validate_userprofile_id(self, value):
        """Validate if the provided userprofile_id exists in the database."""
        if not session.query(UserProfile).filter_by(id=value).first():
            raise serializers.ValidationError("The specified user does not exist.")
        return value

    def validate(self, data):
        """Check if a message with the same type, name, description, status, userprofile_id, and seen already exists."""
        type_ = data.get('type')
        name = data.get('name')
        description = data.get('description')
        status = data.get('status')
        userprofile_id = data.get('userprofile_id')

        existing_message = session.query(Message).filter_by(
            type=type_, name=name, description=description, status=status, userprofile_id=userprofile_id
        ).first()

        if existing_message:
            raise serializers.ValidationError(
                "A message with this type, name, description, status, userprofile_id, and seen status already exists."
            )

        return data



