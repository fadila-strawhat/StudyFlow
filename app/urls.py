from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('assignment/', views.assignment, name='add_assignment'),
    path('complete/<int:id>/', views.complete_assignment, name='complete_assignment'),
    path('delete/<int:id>/', views.delete_assignment, name='delete_assignment'),
    path('edit/<int:id>/', views.edit_assignment, name='edit_assignment'),
    path('signup/', views.signup, name='signup'),
] 