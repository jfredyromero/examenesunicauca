from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.files.storage import FileSystemStorage
import json
from django.views.decorators.csrf import csrf_exempt
from .models import User, Contribution, Teacher, Course, Career, Comment, ContributionImage, Note
from django import forms


class NewContributionForm(forms.Form):
    category = forms.CharField(max_length=512)
    teacher_first_name = forms.CharField(max_length=512)
    teacher_last_name = forms.CharField(max_length=512)
    course_name = forms.CharField(max_length=1024)
    semester = forms.IntegerField()
    year = forms.IntegerField()
    semester_of_year = forms.IntegerField()
    part = forms.IntegerField()
    career_name = forms.CharField(max_length=1024)
    description = forms.CharField(max_length=2048, required=False)


class NewSolutionForm(forms.Form):
    category = forms.CharField(max_length=512)
    teacher_first_name = forms.CharField(max_length=512)
    teacher_last_name = forms.CharField(max_length=512)
    course_name = forms.CharField(max_length=1024)
    career_name = forms.CharField(max_length=1024)
    description = forms.CharField(max_length=2048, required=False)
    solution = forms.CharField(max_length=2048)


class NewNoteForm(forms.Form):
    category = forms.CharField(max_length=512)
    teacher_first_name = forms.CharField(max_length=512)
    teacher_last_name = forms.CharField(max_length=512)
    course_name = forms.CharField(max_length=1024)
    semester = forms.IntegerField()
    year = forms.IntegerField()
    semester_of_year = forms.IntegerField()
    career_name = forms.CharField(max_length=1024)
    description = forms.CharField(max_length=2048, required=False)
    topic = forms.CharField(max_length=2048)


class ContributionEditionForm(forms.Form):
    teacher_first_name = forms.CharField(max_length=512)
    teacher_last_name = forms.CharField(max_length=512)
    course_name = forms.CharField(max_length=1024)
    semester = forms.IntegerField()
    year = forms.IntegerField()
    semester_of_year = forms.IntegerField()
    part = forms.IntegerField()
    career_name = forms.CharField(max_length=1024)
    description = forms.CharField(max_length=2048, required=False)


class SolutionEditionForm(forms.Form):
    teacher_first_name = forms.CharField(max_length=512)
    teacher_last_name = forms.CharField(max_length=512)
    course_name = forms.CharField(max_length=1024)
    career_name = forms.CharField(max_length=1024)
    semester = forms.IntegerField()
    description = forms.CharField(max_length=2048, required=False)


class NoteEditionForm(forms.Form):
    teacher_first_name = forms.CharField(max_length=512)
    teacher_last_name = forms.CharField(max_length=512)
    course_name = forms.CharField(max_length=1024)
    semester = forms.IntegerField()
    year = forms.IntegerField()
    semester_of_year = forms.IntegerField()
    career_name = forms.CharField(max_length=1024)
    description = forms.CharField(max_length=2048, required=False)
    topic = forms.CharField(max_length=2048)


class NewCommentForm(forms.Form):
    content = forms.CharField(max_length=2048)

# Create your views here.

def getPartAsString(part):
    if part == 1:
        return 'Primer Corte'
    elif part == 2:
        return 'Segundo Corte'
    else:
        return 'Tercer Corte'

def getContributionsPage(request, all_contributions):
    paginator = Paginator(all_contributions, 8)
    pag_index = request.GET.get("pag", 1)
    try:
        contributions = paginator.page(pag_index)
    except PageNotAnInteger:
        contributions = paginator.page(1)
    except EmptyPage:
        contributions = paginator.page(paginator.num_pages)
    page_range = contributions.paginator.get_elided_page_range(number=pag_index, on_each_side=2, on_ends=1)
    return contributions, page_range

def index(request):
    contributions = Contribution.objects.filter(
        status=True).order_by("id").reverse()
    contributions, page_range = getContributionsPage(request, contributions)
    return render(request, "ExamenesUnicauca/index.html", {
        "contributions": contributions,
        "page_range": page_range,
        "title": "Inicio"
    })


@login_required()
def moderate(request):
    contributions = Contribution.objects.filter(
        status=False).order_by("id").reverse()
    contributions, page_range = getContributionsPage(request, contributions)
    return render(request, "ExamenesUnicauca/moderate.html", {
        "contributions": contributions,
        "page_range": page_range,
        "title": "Moderar"
    })


def search(request, search_in):
    if search_in == "index":
        status = True
    elif (search_in == "moderate" and not request.user.is_anonymous):
        status = False
    else:
        return HttpResponse(status=404)
    query = request.GET["query"]
    contributions = (Contribution.objects.filter(course__name__icontains=query, status=status) |
                     Contribution.objects.filter(course__career__name__icontains=query, status=status) |
                     Contribution.objects.filter(teacher__first_name__icontains=query, status=status) |
                     Contribution.objects.filter(teacher__last_name__icontains=query, status=status) |
                     Contribution.objects.filter(year__icontains=query, status=status)).order_by("id").reverse()
    contributions, page_range = getContributionsPage(request, contributions)
    title = f'Resultados: "{query}"'
    if status:
        return render(request, "ExamenesUnicauca/index.html", {
            "contributions": contributions,
            "page_range": page_range,
            "title": title,
            "query": query
        })
    else:
        return render(request, "ExamenesUnicauca/moderate.html", {
            "contributions": contributions,
            "page_range": page_range,
            "title": title,
            "query": query
        })


def submit_contribution(request):
    teachers = Teacher.objects.all()
    for teacher in teachers:
            if len(teacher.contributions_of_teacher.filter(status=True))==0: 
                teachers = teachers.exclude(pk=teacher.id)
    careers = Career.objects.all()
    courses = Course.objects.all()
    for course in courses:
            if len(course.contributions_of_course.filter(status=True))==0: 
                courses = courses.exclude(pk=course.id)
    if request.method == "POST":
        if request.POST["category"] == "Parcial":
            form = NewContributionForm(request.POST, request.FILES)
            if form.is_valid():
                # Si no existe el profe, lo crea. Si existe, lo usa
                if not Teacher.objects.filter(first_name=request.POST["teacher_first_name"], last_name=request.POST["teacher_last_name"]).exists():
                    teacher = Teacher(
                        first_name=request.POST["teacher_first_name"], last_name=request.POST["teacher_last_name"])
                    teacher.save()
                else:
                    teacher = Teacher.objects.get(
                        first_name=request.POST["teacher_first_name"], last_name=request.POST["teacher_last_name"])
                # Falso porque entra a ser moderado
                status = False
                # Si no existe la carrera, la crea. Si existe, la usa
                if not Career.objects.filter(name=request.POST["career_name"]).exists():
                    career = Career(name=request.POST["career_name"])
                    career.save()
                else:
                    career = Career.objects.get(
                        name=request.POST["career_name"])
                # Si el curso existe y pertenece al semestre correspondiente, se usa.
                # Si no existe, o existe en otro semestre, se crea un nuevo curso
                if not Course.objects.filter(name=request.POST["course_name"], semester=request.POST["semester"], career=career).exists():
                    course = Course(
                        name=request.POST["course_name"], semester=request.POST["semester"], career=career)
                    course.save()
                else:
                    course = Course.objects.get(
                        name=request.POST["course_name"], semester=request.POST["semester"], career=career)
                # Se añade el profesor a la lista de profesores que dictan el curso
                course.teachers.add(teacher)
                # Año, semestre de año, corte, categoria y descripción digitados
                year = request.POST["year"]
                part = request.POST["part"]
                semester_of_year = request.POST["semester_of_year"]
                description = request.POST["description"]
                category = "Parcial"
                # Se crea el aporte
                contribution = Contribution(category=category, teacher=teacher, status=status, course=course,
                                            year=year, semester_of_year=semester_of_year, part=part, description=description)
                contribution.save()
                # Se crean y almacenan la cantidad de imagenes necesarias, y se asocian a la contribución anterior
                images = request.FILES.getlist("img[]")
                for img in images:
                    fs = FileSystemStorage()
                    image = fs.save(f'{contribution.category}_{contribution.course.name}_{contribution.teacher.first_name} '
                                    f'{contribution.teacher.last_name}_{contribution.year}.'
                                    f'{contribution.semester_of_year}_'+getPartAsString(contribution.part)+'.png', img) 
                    contribution_img = ContributionImage(img=image)
                    contribution_img.save()
                    contribution.images.add(contribution_img)
                    contribution.save()
                return HttpResponseRedirect(reverse("index"))
            else:
                return render(request, "ExamenesUnicauca/submit_contribution.html", {
                    "form": form,
                    "teachers": teachers,
                    "careers": careers,
                    "courses": courses,
                    "semesters": range(1, 11),
                    "message": "Hubo un error al llenar el formulario. Por favor completalo nuevamente."
                })
        elif request.POST["category"] == "Solucionario":
            form = NewSolutionForm(request.POST, request.FILES)
            if form.is_valid():
                # Se trae la info del aporte solucionado
                solution_info = request.POST["solution"].split("-")
                semester_info = solution_info[0].split()
                semester = int(semester_info[1])
                year_info = solution_info[3].strip().split(".")
                year = year_info[0]
                semester_of_year = year_info[1]
                part_info = solution_info[4].strip()
                if part_info == "Primer Corte":
                    part = 1
                elif part_info == "Segundo Corte":
                    part = 2
                else:
                    part = 3
                # Si no existe el profe, lo crea. Si existe, lo usa
                if not Teacher.objects.filter(first_name=request.POST["teacher_first_name"], last_name=request.POST["teacher_last_name"]).exists():
                    teacher = Teacher(
                        first_name=request.POST["teacher_first_name"], last_name=request.POST["teacher_last_name"])
                    teacher.save()
                else:
                    teacher = Teacher.objects.get(
                        first_name=request.POST["teacher_first_name"], last_name=request.POST["teacher_last_name"])
                # Falso porque entra a ser moderado
                status = False
                # Si no existe la carrera, la crea. Si existe, la usa
                if not Career.objects.filter(name=request.POST["career_name"]).exists():
                    career = Career(name=request.POST["career_name"])
                    career.save()
                else:
                    career = Career.objects.get(
                        name=request.POST["career_name"])
                # Si el curso existe y pertenece al semestre correspondiente, se usa.
                # Si no existe, o existe en otro semestre, se crea un nuevo curso
                if not Course.objects.filter(name=request.POST["course_name"], semester=semester, career=career).exists():
                    course = Course(
                        name=request.POST["course_name"], semester=semester, career=career)
                    course.save()
                else:
                    course = Course.objects.get(
                        name=request.POST["course_name"], semester=semester, career=career)
                # Se añade el profesor a la lista de profesores que dictan el curso (Si ya esta agregado antes django no lo agrega de nuevo)
                course.teachers.add(teacher)
                # Se consulta la contribucion solucionada
                try:
                    contribution = Contribution.objects.get(
                        category="Parcial", teacher=teacher, course=course, part=part, year=year, semester_of_year=semester_of_year)
                except Contribution.DoesNotExist:
                    return HttpResponse(status=400)
                description = request.POST["description"]
                category = "Solucionario"
                # Se crea la solucion
                solution = Contribution(category=category, teacher=teacher, course=course, part=part,
                                        status=status, year=year, semester_of_year=semester_of_year, description=description)
                solution.save()
                # Se crean y almacenan la cantidad de imagenes necesarias, y se asocian a la solución anterior
                images = request.FILES.getlist("img[]")
                for img in images:
                    fs = FileSystemStorage()
                    image = fs.save(f'{solution.category}_{solution.course.name}_{solution.teacher.first_name}'
                                    f'{solution.teacher.last_name}_{solution.year}.'
                                    f'{solution.semester_of_year}_'+getPartAsString(solution.part)+'.png', img)
                    solution_img = ContributionImage(img=image)
                    solution_img.save()
                    solution.images.add(solution_img)
                solution.save()
                contribution.solution.add(solution)
                contribution.save()
                return HttpResponseRedirect(reverse("index"))
            else:
                return render(request, "ExamenesUnicauca/submit_contribution.html", {
                    "form": form,
                    "teachers": teachers,
                    "careers": careers,
                    "courses": courses,
                    "semesters": range(1, 11),
                    "message": "Hubo un error al llenar el formulario. Por favor completalo nuevamente."
                })
        else:
            form = NewNoteForm(request.POST, request.FILES)
            if form.is_valid():
                # Si no existe el profe, lo crea. Si existe, lo usa
                if not Teacher.objects.filter(first_name=request.POST["teacher_first_name"], last_name=request.POST["teacher_last_name"]).exists():
                    teacher = Teacher(
                        first_name=request.POST["teacher_first_name"], last_name=request.POST["teacher_last_name"])
                    teacher.save()
                else:
                    teacher = Teacher.objects.get(
                        first_name=request.POST["teacher_first_name"], last_name=request.POST["teacher_last_name"])
                # Falso porque entra a ser moderado
                status = False
                # Si no existe la carrera, la crea. Si existe, la usa
                if not Career.objects.filter(name=request.POST["career_name"]).exists():
                    career = Career(name=request.POST["career_name"])
                    career.save()
                else:
                    career = Career.objects.get(
                        name=request.POST["career_name"])
                # Si el curso existe y pertenece al semestre correspondiente, se usa.
                # Si no existe, o existe en otro semestre, se crea un nuevo curso
                if not Course.objects.filter(name=request.POST["course_name"], semester=request.POST["semester"], career=career).exists():
                    course = Course(
                        name=request.POST["course_name"], semester=request.POST["semester"], career=career)
                    course.save()
                else:
                    course = Course.objects.get(
                        name=request.POST["course_name"], semester=request.POST["semester"], career=career)
                # Se añade el profesor a la lista de profesores que dictan el curso
                course.teachers.add(teacher)
                # Año, semestre de año, corte, categoria y descripción digitados
                year = request.POST["year"]
                topic = request.POST["topic"]
                semester_of_year = request.POST["semester_of_year"]
                description = request.POST["description"]
                category = "Apuntes"
                # Se crea el aporte
                apuntes = Note(category=category, teacher=teacher, status=status, course=course,
                               year=year, semester_of_year=semester_of_year, description=description, topic=topic)
                apuntes.save()
                # Se crean y almacenan la cantidad de imagenes necesarias, y se asocian a la contribución anterior
                images = request.FILES.getlist("img[]")
                for img in images:
                    fs = FileSystemStorage()
                    image = fs.save(f'{apuntes.category}_{apuntes.course.name}_{apuntes.teacher.first_name}'
                                    f'{apuntes.teacher.last_name}_{apuntes.year}_'
                                    f'{apuntes.semester_of_year}_{apuntes.topic}.png', img)
                    apuntes_img = ContributionImage(img=image)
                    apuntes_img.save()
                    apuntes.images.add(apuntes_img)
                    apuntes.save()
                return HttpResponseRedirect(reverse("index"))
            else:
                return render(request, "ExamenesUnicauca/submit_contribution.html", {
                    "form": form,
                    "teachers": teachers,
                    "careers": careers,
                    "courses": courses,
                    "semesters": range(1, 11),
                    "message": "Hubo un error al llenar el formulario. Por favor completalo nuevamente."
                })
    else:
        return render(request, "ExamenesUnicauca/submit_contribution.html", {
            "teachers": teachers,
            "careers": careers,
            "courses": courses,
            "semesters": range(1, 10)
        })


@login_required()
def edit_contribution(request, contribution_id):
    try:
        contribution = Contribution.objects.get(pk=contribution_id)
    except Contribution.DoesNotExist:
        return HttpResponse(status=404)
    teachers = Teacher.objects.all()
    careers = Career.objects.all()
    courses = Course.objects.all()
    if request.method == "POST":
        if contribution.category == "Parcial":
            form = ContributionEditionForm(request.POST)
            if form.is_valid():
                teacher = Teacher.objects.get(
                    first_name=contribution.teacher.first_name, last_name=contribution.teacher.last_name)
                course = Course.objects.get(
                    name=contribution.course.name, semester=contribution.course.semester, career=contribution.course.career)
                career = Career.objects.get(
                    name=contribution.course.career.name)
                # Si las contribuciones del profesor son <= 1, el profesor se elimina
                # Si el profesor tiene 1 contribucion, significa que es la que estamos editando
                if len(teacher.contributions_of_teacher.all()) <= 1:
                    teacher.delete()
                # Si el curso tiene <= 1 contribuciones, el curso se elimina
                # Si el curso tiene 1 contribucion, es la que se esta editando
                if len(course.contributions_of_course.all()) <= 1:
                    course.delete()
                # Si la carrera tiene 0 cursos, se elimina
                # Ya NO tiene minimo 1 curso porque el curso se elimino en la condicion anterior
                if len(career.courses_of_career.all()) == 0:
                    career.delete()
                # El procedimiento que sigue a continuacion es el mismo que se realiza cuando se crea un nuevo aporte
                if not Teacher.objects.filter(first_name=request.POST["teacher_first_name"], last_name=request.POST["teacher_last_name"]).exists():
                    teacher = Teacher(
                        first_name=request.POST["teacher_first_name"], last_name=request.POST["teacher_last_name"])
                    teacher.save()
                else:
                    teacher = Teacher.objects.get(
                        first_name=request.POST["teacher_first_name"], last_name=request.POST["teacher_last_name"])
                status = False
                if not Career.objects.filter(name=request.POST["career_name"]).exists():
                    career = Career(name=request.POST["career_name"])
                    career.save()
                else:
                    career = Career.objects.get(
                        name=request.POST["career_name"])
                if not Course.objects.filter(name=request.POST["course_name"], semester=request.POST["semester"]).exists():
                    course = Course(
                        name=request.POST["course_name"], semester=request.POST["semester"], career=career)
                    course.save()
                else:
                    course = Course.objects.get(
                        name=request.POST["course_name"], semester=request.POST["semester"], career=career)
                course.teachers.add(teacher)
                year = request.POST["year"]
                part = request.POST["part"]
                semester_of_year = request.POST["semester_of_year"]
                description = request.POST["description"]
                # Se guardan los nuevos cambios
                contribution.teacher = teacher
                contribution.status = status
                contribution.course = course
                contribution.year = year
                contribution.semester_of_year = semester_of_year
                contribution.part = part
                contribution.description = description
                contribution.save()
                # Las imagenes y la categoria no se pueden editar
                images = contribution.images.all()
                for img in images:
                    fs = FileSystemStorage()
                    # Guardo las imagenes en su nueva ubicación
                    image = fs.save(f'{contribution.category}_{contribution.course.name}_{contribution.teacher.first_name} '
                                    f'{contribution.teacher.last_name}_{contribution.year}_'
                                    f'{contribution.semester_of_year}_'+getPartAsString(contribution.part)+'_.png', img.img)
                    # Se eliminan las imagenes anteriores
                    img.img.delete()
                    # Se guarda el nuevo objeto imagen sobre el anterior
                    img.img = image
                    img.save()
                contribution.save()
                return HttpResponseRedirect(reverse("contribution_view", args=[contribution_id]))
            else:
                return render(request, "ExamenesUnicauca/edit_contribution.html", {
                    "form": form,
                    "teachers": teachers,
                    "careers": careers,
                    "courses": courses
                })
        elif contribution.category == "Solucionario":
            form = SolutionEditionForm(request.POST)
            if form.is_valid():
                teacher = Teacher.objects.get(
                    first_name=contribution.teacher.first_name, last_name=contribution.teacher.last_name)
                course = Course.objects.get(
                    name=contribution.course.name, semester=contribution.course.semester, career=contribution.course.career)
                career = Career.objects.get(
                    name=contribution.course.career.name)
                # Si las contribuciones del profesor son <= 1, el profesor se elimina
                # Si el profesor tiene 1 contribucion, significa que es la que estamos editando
                if len(teacher.contributions_of_teacher.all()) <= 1:
                    teacher.delete()
                # Si el curso tiene <= 1 contribuciones, el curso se elimina
                # Si el curso tiene 1 contribucion, es la que se esta editando
                if len(course.contributions_of_course.all()) <= 1:
                    course.delete()
                # Si la carrera tiene 0 cursos, se elimina
                # Ya NO tiene minimo 1 curso porque el curso se elimino en la condicion anterior
                if len(career.courses_of_career.all()) == 0:
                    career.delete()
                # El procedimiento que sigue a continuacion es el mismo que se realiza cuando se crea un nuevo aporte
                if not Teacher.objects.filter(first_name=request.POST["teacher_first_name"], last_name=request.POST["teacher_last_name"]).exists():
                    teacher = Teacher(
                        first_name=request.POST["teacher_first_name"], last_name=request.POST["teacher_last_name"])
                    teacher.save()
                else:
                    teacher = Teacher.objects.get(
                        first_name=request.POST["teacher_first_name"], last_name=request.POST["teacher_last_name"])
                status = False
                if not Career.objects.filter(name=request.POST["career_name"]).exists():
                    career = Career(name=request.POST["career_name"])
                    career.save()
                else:
                    career = Career.objects.get(
                        name=request.POST["career_name"])
                if not Course.objects.filter(name=request.POST["course_name"], semester=request.POST["semester"]).exists():
                    course = Course(
                        name=request.POST["course_name"], semester=request.POST["semester"], career=career)
                    course.save()
                else:
                    course = Course.objects.get(
                        name=request.POST["course_name"], semester=request.POST["semester"], career=career)
                course.teachers.add(teacher)
                description = request.POST["description"]
                # Se guardan los nuevos cambios
                contribution.teacher = teacher
                contribution.status = status
                contribution.course = course
                contribution.description = description
                contribution.save()
                # Las imagenes y la categoria no se pueden editar
                images = contribution.images.all()
                for img in images:
                    fs = FileSystemStorage()
                    # Guardo las imagenes en su nueva ubicación
                    image = fs.save(f'{contribution.category}_{contribution.course.name}_{contribution.teacher.first_name} '
                                    f'{contribution.teacher.last_name}_{contribution.year}_'
                                    f'{contribution.semester_of_year}_'+getPartAsString(contribution.part)+'_.png', img.img)
                    # Se eliminan las imagenes anteriores
                    img.img.delete()
                    # Se guarda el nuevo objeto imagen sobre el anterior
                    img.img = image
                    img.save()
                contribution.save()
                return HttpResponseRedirect(reverse("contribution_view", args=[contribution_id]))
            else:
                return render(request, "ExamenesUnicauca/edit_contribution.html", {
                    "form": form,
                    "teachers": teachers,
                    "careers": careers,
                    "courses": courses
                })
        else:
            form = NoteEditionForm(request.POST)
            if form.is_valid():
                teacher = Teacher.objects.get(
                    first_name=contribution.teacher.first_name, last_name=contribution.teacher.last_name)
                course = Course.objects.get(
                    name=contribution.course.name, semester=contribution.course.semester, career=contribution.course.career)
                career = Career.objects.get(
                    name=contribution.course.career.name)
                # Si las contribuciones del profesor son <= 1, el profesor se elimina
                # Si el profesor tiene 1 contribucion, significa que es la que estamos editando
                if len(teacher.contributions_of_teacher.all()) <= 1:
                    teacher.delete()
                # Si el curso tiene <= 1 contribuciones, el curso se elimina
                # Si el curso tiene 1 contribucion, es la que se esta editando
                if len(course.contributions_of_course.all()) <= 1:
                    course.delete()
                # Si la carrera tiene 0 cursos, se elimina
                # Ya NO tiene minimo 1 curso porque el curso se elimino en la condicion anterior
                if len(career.courses_of_career.all()) == 0:
                    career.delete()
                # El procedimiento que sigue a continuacion es el mismo que se realiza cuando se crea un nuevo aporte
                if not Teacher.objects.filter(first_name=request.POST["teacher_first_name"], last_name=request.POST["teacher_last_name"]).exists():
                    teacher = Teacher(
                        first_name=request.POST["teacher_first_name"], last_name=request.POST["teacher_last_name"])
                    teacher.save()
                else:
                    teacher = Teacher.objects.get(
                        first_name=request.POST["teacher_first_name"], last_name=request.POST["teacher_last_name"])
                status = False
                if not Career.objects.filter(name=request.POST["career_name"]).exists():
                    career = Career(name=request.POST["career_name"])
                    career.save()
                else:
                    career = Career.objects.get(
                        name=request.POST["career_name"])
                if not Course.objects.filter(name=request.POST["course_name"], semester=request.POST["semester"]).exists():
                    course = Course(
                        name=request.POST["course_name"], semester=request.POST["semester"], career=career)
                    course.save()
                else:
                    course = Course.objects.get(
                        name=request.POST["course_name"], semester=request.POST["semester"], career=career)
                course.teachers.add(teacher)
                year = request.POST["year"]
                topic = request.POST["topic"]
                semester_of_year = request.POST["semester_of_year"]
                description = request.POST["description"]
                # Se guardan los nuevos cambios
                contribution.teacher = teacher
                contribution.status = status
                contribution.course = course
                contribution.year = year
                contribution.semester_of_year = semester_of_year
                contribution.description = description
                contribution.save()
                apunte = Note.objects.get(pk=contribution.id)
                apunte.topic = topic
                apunte.save()
                # Las imagenes y la categoria no se pueden editar
                images = contribution.images.all()
                for img in images:
                    fs = FileSystemStorage()
                    # Guardo las imagenes en su nueva ubicación
                    image = fs.save(f'{apunte.category}_'
                                    f'{apunte.course.name}_{apunte.teacher.first_name} '
                                    f'{apunte.teacher.last_name}_{apunte.year}.'
                                    f'{apunte.semester_of_year}_{apunte.topic}.png', img.img)
                    # Se eliminan las imagenes anteriores
                    img.img.delete()
                    # Se guarda el nuevo objeto imagen sobre el anterior
                    img.img = image
                    img.save()
                contribution.save()
                return HttpResponseRedirect(reverse("contribution_view", args=[contribution_id]))
            else:
                return render(request, "ExamenesUnicauca/edit_contribution.html", {
                    "form": form,
                    "teachers": teachers,
                    "careers": careers,
                    "courses": courses
                })
    else:
        return render(request, "ExamenesUnicauca/edit_contribution.html", {
            "contribution": contribution,
            "teachers": teachers,
            "careers": careers,
            "courses": courses
        })


def add_comment(request):
    if request.method != "POST":
        return HttpResponse(status=400)
    contribution_id = request.POST["contribution_commented"]
    try:
        contribution = Contribution.objects.get(pk=contribution_id)
    except Contribution.DoesNotExist:
        return HttpResponse(status=404)
    form = NewCommentForm(request.POST)
    if form.is_valid():
        content = request.POST["content"]
        comment = Comment(content=content)
        comment.save()
        contribution.comments.add(comment)
        contribution.save()
        return HttpResponseRedirect(reverse("contribution_view", args=[contribution_id]))
    else:
        return render(request, "ExamenesUnicauca/contribution.html", {
            "contributions": contribution,
            "form": form
        })


@csrf_exempt
def get_contributions_to_solutions(request):

    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    data = json.loads(request.body)

    contributions = Contribution.objects.filter(
        category="Parcial", status=True)

    if data.get("career_name") != "":
        career_name = data["career_name"]
        q1 = Contribution.objects.filter(
            course__career__name__icontains=career_name)
        contributions = contributions & q1
    if data.get("teacher_first_name") != "":
        teacher_first_name = data["teacher_first_name"]
        q2 = Contribution.objects.filter(
            teacher__first_name__icontains=teacher_first_name)
        contributions = contributions & q2
    if data.get("teacher_last_name") != "":
        teacher_last_name = data["teacher_last_name"]
        q3 = Contribution.objects.filter(
            teacher__last_name__icontains=teacher_last_name)
        contributions = contributions & q3
    if data.get("course_name") != "":
        course_name = data["course_name"]
        q4 = Contribution.objects.filter(course__name__icontains=course_name)
        contributions = contributions & q4

    return JsonResponse([contribution.serialize() for contribution in contributions], safe=False)


@csrf_exempt
def contribution_view(request, contribution_id):
    try:
        contribution = Contribution.objects.get(pk=contribution_id)
    except Contribution.DoesNotExist:
        return HttpResponse(status=404)
    if request.method == "PUT":
        data = json.loads(request.body)
        if data.get("flag") is not None:
            flag = data["flag"]
            if flag:
                contribution.status = True
                images = contribution.images.all()
                aux = 1
                for img in images:
                    fs = FileSystemStorage()
                    # Guardo las imagenes en su nueva ubicación
                    if contribution.category == 'Parcial' or contribution.category == 'Solucionario':  
                        image = fs.save(f'{contribution.category}/{contribution.course.career.name}'
                                        f'/Semestre {contribution.course.semester}/{contribution.course.name}'
                                        f'/{contribution.teacher.first_name} {contribution.teacher.last_name}'
                                        f'/{contribution.year}.{contribution.semester_of_year}/'
                                        f'{contribution.course.name}_{contribution.teacher.first_name}'
                                        f'{contribution.teacher.last_name}_{contribution.year}.'
                                        f'{contribution.semester_of_year}_'+getPartAsString(contribution.part)+f'_{aux}.png', img.img)
                    else:
                        apunte = Note.objects.get(pk=contribution.id)
                        image = fs.save(f'{apunte.category}/{apunte.course.career.name}'
                                        f'/Semestre {apunte.course.semester}/{apunte.course.name}'
                                        f'/{apunte.teacher.first_name} {apunte.teacher.last_name}'
                                        f'/{apunte.year}.{apunte.semester_of_year}/'
                                        f'{apunte.course.name}_{apunte.teacher.first_name}'
                                        f'{apunte.teacher.last_name}_{apunte.year}.'
                                        f'{apunte.semester_of_year}_{apunte.topic}_{aux}.png', img.img)
                    aux += 1
                    # Se eliminan las imagenes anteriores
                    img.img.delete()
                    # Se guarda el nuevo objeto imagen sobre el anterior
                    img.img = image
                    img.save()
                contribution.save()
            else:
                teacher = Teacher.objects.get(
                    first_name=contribution.teacher.first_name, last_name=contribution.teacher.last_name)
                course = Course.objects.get(
                    name=contribution.course.name, semester=contribution.course.semester, career=contribution.course.career)
                career = Career.objects.get(
                    name=contribution.course.career.name)
                images = contribution.images.all()
                for img in images:
                    img.img.delete()
                    image_to_delete = ContributionImage.objects.get(
                        img=img.img)
                    image_to_delete.delete()
                if len(teacher.contributions_of_teacher.all()) <= 1:
                    teacher.delete()
                if len(course.contributions_of_course.all()) <= 1:
                    course.delete()
                if len(career.courses_of_career.all()) == 0:
                    career.delete()
                contribution.delete()
            return HttpResponse(status=201)
        else:
            return HttpResponse(status=404)
    else:
        if contribution.status:
            contribution.visits += 1
            contribution.save()
            return render(request, "ExamenesUnicauca/contribution.html", {
                "contribution": contribution
            })
        elif request.user.is_authenticated:
            return render(request, "ExamenesUnicauca/contribution.html", {
                "contribution": contribution
            })
        else:
            return HttpResponse(status=404)


def career_view(request, career_name):
    career = Career.objects.get(name=career_name)
    courses = Course.objects.filter(career=career)
    courses_per_semester = []
    courses_per_semester.append(len(courses.filter(semester=1)))
    courses_per_semester.append(len(courses.filter(semester=2)))
    courses_per_semester.append(len(courses.filter(semester=3)))
    courses_per_semester.append(len(courses.filter(semester=4)))
    courses_per_semester.append(len(courses.filter(semester=5)))
    courses_per_semester.append(len(courses.filter(semester=6)))
    courses_per_semester.append(len(courses.filter(semester=7)))
    courses_per_semester.append(len(courses.filter(semester=8)))
    courses_per_semester.append(len(courses.filter(semester=9)))
    courses_per_semester.append(len(courses.filter(semester=10)))
    return render(request, "ExamenesUnicauca/semesters.html", {
        "career": career_name,
        "courses": courses_per_semester
    })


def semester_view(request, career_name, semester):
    if request.method != "GET":
        return JsonResponse({"error": "GET request required."}, status=400)
    career = Career.objects.get(name=career_name)
    courses = career.courses_of_career.filter(semester=semester)
    for course in courses:
        if len(course.contributions_of_course.filter(status=True))==0: 
            courses = courses.exclude(pk=course.id)
    return JsonResponse([course.serialize() for course in courses], safe=False)


def course_view(request, course_name, teacher_name):
    teachers = Teacher.objects.all()
    for teacher in teachers:
        if teacher.first_name+' '+teacher.last_name == teacher_name:
            final_teacher = teacher
    course = final_teacher.courses_of_teacher.get(name=course_name)
    contributions = Contribution.objects.filter(
        teacher=final_teacher, course=course).order_by("id").reverse()
    contributions, page_range = getContributionsPage(request, contributions)
    return render(request, "ExamenesUnicauca/index.html", {
        "contributions": contributions,
        "page_range": page_range,
        "title": course_name
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "ExamenesUnicauca/login.html", {
                "message": "Nombre de usuario y/o contraseña inválido"
            })
    else:
        return render(request, "ExamenesUnicauca/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


@login_required
def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        secret = request.POST["secret"]

        if secret != "jhon":
            return render(request, "ExamenesUnicauca/register.html", {
                "message": "Si deseas tener una nueva cuenta, comunicate con el administrador"
            })
        else:
            # Ensure password matches confirmation
            password = request.POST["password"]
            confirmation = request.POST["confirmation"]
            if password != confirmation:
                return render(request, "ExamenesUnicauca/register.html", {
                    "message": "Las contraseñas deben coincidir"
                })

            # Attempt to create new user
            try:
                user = User.objects.create_user(username, email, password)
                user.save()
            except IntegrityError:
                return render(request, "ExamenesUnicauca/register.html", {
                    "message": "Nombre de usuario existente"
                })
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "ExamenesUnicauca/register.html")