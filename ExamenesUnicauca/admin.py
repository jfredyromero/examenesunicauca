from django.contrib import admin
from .models import User, Contribution, Teacher, Course, Career, Comment, ContributionImage, Note

# Register your models here.

admin.site.register(User)
admin.site.register(Teacher)
admin.site.register(Course)
admin.site.register(Contribution)
admin.site.register(Career)
admin.site.register(Comment)
admin.site.register(ContributionImage)
admin.site.register(Note)

