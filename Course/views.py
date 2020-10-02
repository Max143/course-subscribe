from django.shortcuts import render, get_object_or_404
from .models import Course, Lesson
from django.views.generic import ListView, DetailView, View
from Membership.models import *


def Home(request):
    return render(request, 'course/home.html')

    
class CourseListView(ListView):
    model = Course
    template_name = 'course_list.html'

class CourseDetailView(DetailView):
    model = Course
    template_name = 'course_detail.html'



class LesssonListView(View):
     def get(self, request, course_slug, lesson_slug, *args, **kwargs):
        course = get_object_or_404(Course, slug=course_slug)
        lesson = get_object_or_404(Lesson, slug=lesson_slug)
        
        user_membership = get_object_or_404(UserMembership, user=request.user)
        print(user_membership)
        
        user_membership_type = user_membership.membership.membership_type
        print(user_membership_type)

        course_allowed_mem_types = course.allowed_memberships.all()
        print(course_allowed_mem_types)

        context = { 'object': None }

        if course_allowed_mem_types.filter(membership_type=user_membership_type).exists():
            context = {'object': lesson}
            print(lesson)
       
        return render(request, "course/lesson_detail.html", context)