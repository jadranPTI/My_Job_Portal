from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Job, CustomUser, JobApplication, TrainerService

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id","email", "password", "role"]
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            role=validated_data.get('role', 'candidate')  
        )
        user.set_password(validated_data['password'])  
        user.save()
        return user
            

class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = '__all__'
        read_only_fields = ("posted_by",)

class JobApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobApplication
        fields = "__all__"
        read_only_fields = ('candidate', 'status')

class TrainerServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainerService
        fields = '__all__'
        read_only_fields = ('trainer',) 

        # def create(self, validate_data):
        #     return TrainerService.objects.create(**validate_data)