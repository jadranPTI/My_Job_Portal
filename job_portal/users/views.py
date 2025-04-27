from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer, JobSerializer, JobApplicationSerializer, TrainerServiceSerializer
from .models import Job, CustomUser, JobApplication, TrainerService
from django.shortcuts import get_object_or_404
from .permissions import IsAdminUser, IsCandidate, IsRecruiter, IsAdminorRecruiter

User = get_user_model()

@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_only_use(request):
    if request.user.role != 'admin':
        return Response({"error": "Access Denied"}, status=403)
    return Response({"message": "Welcome, Admin! This is your dashboard view."})


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsRecruiter])
def recruiter_only_view(request):
    if request.user.role != 'recruiter':
        return Response({"error": "Access Denied"}, status=403)
    return Response({"message": "Hello, Recruiter! You can post and manage job listings."})

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsCandidate])
def candidate_only_view(request):
    if request.user.role != 'candidate':
        return Response({"error": "Access Denied"}, status=403)
    return Response({"message": "Welcome, Candidate! You can search and apply for jobs."})

class RegisterUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # permission_classes = [AllowAny]

    def perform_create(self, serializer):
        serializer.save()  # Serializer ka create method password hash karega

class LoginView(APIView):
    # permission_classes = [AllowAny]
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        user = User.objects.filter(email=email).first()
        if user is None or not user.check_password(password):
            return Response({"error": "Invalid credentials"}, status=400)

        refresh = RefreshToken.for_user(user)
        return Response({
            "message": "Login Successful",
            "user" : UserSerializer(user).data,
            "tokens": {
                "refresh" : str(refresh),
                "access" : str(refresh.access_token),
            }
            
        })
    
class UserDetailView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class AdminJobView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    def post(self, request):
        request.data['posted_by'] = request.user.id
        serializer = JobSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class JobListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminorRecruiter]

    def get(self, request):
        jobs = Job.objects.filter(status="active")
        serializer = JobSerializer(jobs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = JobSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(posted_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class JobUpdateDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        job = get_object_or_404(Job, pk=pk)
        if request.user.role != 'admin' and job.posted_by != request.user:
            return Response({"error" : "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
        serializer = JobSerializer(job, data=request.data, partial = True)
        if serializer.is_valid():
            serializer.save()
            return Response({serializer.data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # def patch(self, request, pk):
    #     job = get_object_or_404(Job, pk=pk)
    #     serializer = JobSerializer(instance=job, data=request.data, partial=True)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_200_OK)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        job = get_object_or_404(Job, pk=pk)
        if request.user.role != 'admin' and job.posted_by != request.user:
            return Response({"error" : "Permission denied"}, status= status.HTTP_403_FORBIDDEN)
        job.delete()
        return Response({"message": "Job deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


class JobApplicationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, job_id):
        user = request.user

        if request.user.role != 'candidate':
            return Response({"Error" : "Only candidates can apply for jobs"}, status=status.HTTP_403_FORBIDDEN)
        
        job = get_object_or_404(job,pk=job_id)

        if JobApplication.objects.filter(job=job, candidate = request.user).exists():
            return Response({"Error": "You have already applied for this job"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = JobApplicationSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save(job=job, applicant = user)
            return Response({serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # try:
        #     job = Job.objects.all(id=job_id)
        # except Job.DoesNotExist:
        #     return Response({"Error": "Job not found"},status=status.HTTP_404_NOT_FOUND)
        
        
class CandidateApplicationsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != 'candidate':
            return Response({"error" : "Access Denied"}, status=status.HTTP_403_FORBIDDEN)
        user = request.user

        # if user.role != "recruiter":
        #     return Response({"error": "Only recruiters can view job applications"}, status=status.HTTP_403_FORBIDDEN)
        application = JobApplication.objects.filter(candidate=request.user)
        serializer = JobApplicationSerializer(application, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TrainerServiceView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.role != 'trainer':
            return Response({'error' : "Only trainer can add services"}, status= status.HTTP_403_FORBIDDEN)
        
        serializer = TrainerServiceSerializer(data= request.data)
        if serializer.is_valid():
            serializer.save(trainer= request.user)
            return Response(serializer.data, status= status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        services = TrainerService.objects.filter(trainer = request.user)
        serializer = TrainerServiceSerializer(services, many=True)
        return Response(serializer.data)
    

class AllTrainerServicesView(APIView):
    def get(self, request):
        services = TrainerService.objects.filter(is_active=True)
        serializer = TrainerServiceSerializer(services, many=True)
        return Response(serializer.data)


class AdminTrainingView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        trainings = TrainerService.objects.all()
        serializer = TrainerServiceSerializer(trainings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = TrainerServiceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, pk):
        training = get_object_or_404(TrainerService, pk=pk)
        serializer = TrainerServiceSerializer(training, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        training = get_object_or_404(TrainerService, pk=pk)
        training.delete()
        return Response({'message' : "Training Deleted!"}, status=status.HTTP_204_NO_CONTENT)