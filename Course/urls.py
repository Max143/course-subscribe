from django.urls import path
from .views import CourseListView, CourseDetailView, LesssonListView
from . import views

app_name = 'Course'

urlpatterns = [

    path('', views.Home, name='home'),
    path('courses/', CourseListView.as_view(), name='list'),
    path('course/<slug>/', CourseDetailView.as_view(), name='detail'),  
    path('<course_slug>/<lesson_slug>/', LesssonListView.as_view(), name='lesson-detail'),  

]
