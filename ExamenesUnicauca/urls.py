from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("contribution/<int:contribution_id>", views.contribution_view, name="contribution_view"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
    path("submit/", views.submit_contribution, name="submit_contribution"),
    path("career/<str:career_name>", views.career_view, name="career_view"),
    path("career/<str:career_name>/<int:semester>", views.semester_view, name="semester_view"),
    path("course/<str:course_name>/<str:teacher_name>", views.course_view, name="course_view"),
    path("moderate/", views.moderate, name="moderate"),
    path("comment/", views.add_comment, name="add_comment"),
    path("search/<str:search_in>", views.search, name="search"),
    path("edit/<int:contribution_id>", views.edit_contribution, name="edit_contribution"),
    path("solutions/", views.get_contributions_to_solutions, name="get_contributions_to_solutions")
]