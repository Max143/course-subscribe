from django.contrib import admin
from .models import *


class CourseAdmin(models.AdminModel):
    list_display = ('title','description','timestamp',)
    search_fileds = ('title',)
    prepopulated_fields = {'slug':('title',)}

admin.site.register(Course, CourseAdmin)
class LessonAdmin(models.AdminModel):
    list_display = ('title','course','position','timestamp',)
    search_fields = ('cource',)
    prepopulated_fields = {'slug':('title',)}


admin.site.register(Lesson, LessonAdmin)

