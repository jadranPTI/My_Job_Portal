from django.urls import path
from .views import RegisterUserView, LoginView, UserDetailView
from .views import admin_only_use, recruiter_only_view, candidate_only_view, JobListCreateView, JobUpdateDeleteView, JobApplicationView, CandidateApplicationsView, TrainerServiceView, AllTrainerServicesView, AdminTrainingView

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('jobs/', JobListCreateView.as_view(), name='job-list-create'),
    path('jobs/<int:pk>/', JobUpdateDeleteView.as_view(), name='job-detail-view'),
    path('jobs/<int:job_id>/apply', JobApplicationView.as_view(), name='job-apply'),
    path('my-applications/', CandidateApplicationsView.as_view(), name="my-applications"),
    path('trainer/services/', TrainerServiceView.as_view(), name="trainer-services"),
    path('services/', AllTrainerServicesView.as_view(), name='all-services'),
    path('admin/trainings/', AdminTrainingView.as_view(), name='all-trainings'),
    path('admin/trainings/<int:pk>/',AdminTrainingView.as_view(), name= 'training-detail-view')
]
