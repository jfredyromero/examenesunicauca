from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models

def user_directory_path(instance, filename):
    return f'{instance.contribution_of_image.category}/{instance.contribution_of_image.course.career.name}'\
            f'/Semestre {instance.contribution_of_image.course.semester}/{instance.contribution_of_image.course.name}'\
            f'/{instance.contribution_of_image.teacher.first_name} {instance.contribution_of_image.teacher.last_name}'\
            f'/{instance.contribution_of_image.year}.{instance.contribution_of_image.semester_of_year}/{filename}'

# Create your models here.

class User(AbstractUser):
    pass

class Teacher(models.Model):
    first_name = models.CharField(max_length=512)
    last_name = models.CharField(max_length=512)
    def __str__(self):
        return f"Profesor {self.id}: {self.first_name} {self.last_name}"

class Career(models.Model):
    name = models.CharField(max_length=1024, unique=True)
    def __str__(self):
        return f"Carrera {self.id}: {self.name}"

class Course(models.Model):
    name = models.CharField(max_length=1024)
    semester = models.IntegerField()
    # Si se elimina la carrera, se eliminan los cursos 
    career = models.ForeignKey(Career, on_delete=models.CASCADE, related_name="courses_of_career")
    teachers = models.ManyToManyField(Teacher, blank=True, related_name="courses_of_teacher")
    def __str__(self):
        return f"Curso {self.id}: {self.name}"
    def serialize(self):
        active_teachers = self.teachers.all()
        print(active_teachers)
        for teacher in active_teachers:
            if len(teacher.contributions_of_teacher.filter(course=self, status=True))==0: 
                active_teachers = active_teachers.exclude(pk=teacher.id)
        print(active_teachers)
        return {
            "name": self.name,
            "semester": self.semester,
            "career": self.career.name,
            "teachers": [f'{teacher.first_name} {teacher.last_name}' for teacher in active_teachers],
            "contributions_of_teachers": [f'{len(teacher.contributions_of_teacher.filter(course=self))}' for teacher in active_teachers]
        }

class Comment(models.Model):
    content = models.CharField(max_length=2048)
    timestamp = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Comentario {self.id}: {self.content}"

class ContributionImage(models.Model):
    img = models.ImageField(upload_to=user_directory_path, max_length=4096)
    def __str__(self):
        return f"Image {self.id}: Saved on {user_directory_path}"

class Contribution(models.Model):
    category = models.CharField(max_length=512)
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, related_name="contributions_of_teacher")
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, related_name="contributions_of_course")
    part = models.IntegerField(null=True)
    status = models.BooleanField()
    year = models.IntegerField()
    semester_of_year = models.IntegerField()
    images = models.ManyToManyField(ContributionImage, blank=True, related_name="contribution_of_image")
    description = models.CharField(max_length=2048, blank=True)
    comments = models.ManyToManyField(Comment, blank=True, related_name="contribution_of_comment")
    timestamp = models.DateTimeField(auto_now_add=True)
    visits = models.IntegerField(default=0)
    solution = models.ManyToManyField('self', blank=True, symmetrical=False, related_name="contribution_of_solution")
    def __str__(self):
        return f"{self.category}: {self.course.career.name} - {self.course.name} - {self.teacher.first_name} {self.teacher.last_name} - {self.year}.{self.semester_of_year}"
    def serialize(self):
        if self.part == 1:
            part = 'Primer Corte'
        elif self.part == 2:
            part = 'Segundo Corte'
        else:
            part = 'Tercer Corte'
        return {
            "teacher": f'{self.teacher.first_name} {self.teacher.last_name}',
            "course": self.course.name,
            "semester": self.course.semester,
            "career": self.course.career.name,
            "year": self.year,
            "semester_of_year": self.semester_of_year,
            "part": part
        }
    @property
    def apuntes(self):
        if self.note:
            return self.note
        else:
            return None

class Note(Contribution):
    topic = models.CharField(max_length=2048)
    part = None
    def __str__(self):
        return f"Apuntes {self.id}: {self.course.career.name} - {self.course.name} - {self.topic} - {self.teacher.first_name} {self.teacher.last_name}"
