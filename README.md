# Examenes Unicauca - Web Page

## Introduction
This repository contains the source code of the *Examenes Unicauca - Web Page*. The University of Cauca from Popayán, Colombia has a lot of programs (in this projects called *"careers"*) you can being part of. Each one of these programs has some courses and the students have to enroll and course every one of them (as the program stipulates it) in order to get to be a professional. Some of those courses are given by some teachers who love creating hard tests, and there are sometimes that students require some example tests to properly get prepared and know what to expect at test time. The best examples test are usually from past courses (the same course but some semesters before), but unfortunately some teachers keep their test for their own, avoiding students to share them; or if the student gets to keep the tests, as long as time pass, these get lost unallowing new students to properly get prepared for tests and many times leading to students having problems to pass their courses.

## How does it works?
Examenes Unicauca - Web Page battles the presented issue, storing  images of tests in a database, and sorting them out having this properties in mind:

- **Teacher:** The teacher who gives the course where the test was made

- **Course:** The course where the test was made

- **Career:** The program where the course is given

- **Semester:** The semester where the student is schedule to see the course

- **Year:** The year when the test was made

- **Semester of year:** The semester of the year when the test was made ( i.e. January to June or July to December)

- **Part:** The part of the course that is being tested. In Colombia, college courses are generally split into three parts, this leading to having three tests per course.

Each *test* uploaded to the web page is called a contribution.

Examenes Unicauca also allows users to store the *solution* for every test. For that reason, every test could be related to a solution if it exists and has been uploaded to the page.

Theres are sometimes where tests and solutions are not enough for a student to properly get prepared, that is why Examenes Unicauca also allows users to store their *notes* of the course (i.e. images of his notebook).

Having this in mind, a contribution could be classified in three categories:
- Test (called in project "Parcial")
- Solution (called in project "Solucionario")
- Note (called in project "Apuntes")

Each contribution is able to store as many images as needed.

## Users
There are two types of user:
#### Conventional user:
It is the user who only wants to see the page, looks for contributions he needs, and upload contributions to the web page.

#### Super user:
It is the user who is responsible for moderating the contributions. The contributions has a state: True if it has been accepted and False if it has not been moderated. This user is able to check all contributions that conventional users have made, before posting them in Home Page. If the contribution is wrong, he is responsible for editing them or deleting them if necessary. When this user has checked the contribution and decides it is okay, he is able to accept the contribution, changing its state to True and automatically posting them on the home page.

A super user shall only be created for another super user that has the password for this option. It is an important role, because he is the one who is responsible for having everything okay.

## Distinctiveness and Complexity

### Why this?
This project was the main reason why I took the course, because I'm about to finish my studies and there were a lot of times that I needed a good preparation for some tests, but I couldn't because I didn't have enough practice when I was getting prepared. With the web page, every student could make his own contribution and help students he doesn't even know. 

Also, It is very common that some introverted and shy students don't have friends in the above semesters to help them by handling their notes or past tests. The web page solves this issue, because these students are now able to get every resource other students have, and allows them to have the same chance to get well prepared as every other student. That's the main reason why the web page doesn't require an user account and everything is anonymous.

Having in mind that every person is able to make his contribution, the web page needs to handle this information and make sure it is veridic. That's why the moderation function exists. When a conventional user is trying to make his contribution to the page, it's helped by the datalist of the inputs' form, avoiding the creation of new instances of a model just for having a single character of difference. However, if the conventional user decides to not follow this help, there is still the option of the super users for editing the contribution in order to create new instances just when necessary or use the ones that already exist. 

When creating a solution, a test is necessary related to it. If the page stores thousands of test, the select input that allows the conventional user to choose the related test will have thousands of options and it will be very frustrating to the user. That's why that select input fetches the tests that match the filled inputs before itself, and filters out the ones that don't, making this option a lot easier.

When a conventional user is searching for some specific contribution, he may think that he should check all the pagination pages until he finds what's looking for. In order to make this a straightforward process, a search input has been added at the top of the page, allowing users to search for any contribution by knowing the teacher's first or last name, the name of the course, the name of the program (career's name) or even the year the contribution was made. It couldn't be easier!

Another way to filter contributions out is provided by the semesters url. This page displays all registered semesters of a specific program, and fetches all courses and all teachers related to it... in a dynamic way! Enjoy this process with no need of reloading the entire page.

Last but not least, a final great advantage that the web page provides is that it automatically sorts all the images of contributions, storing them in special paths and making it easier to look for a specific one. Plus, the web page also has a great mobile version that fits every screen size, and it even has its own logo! Pretty cool!.

### What is in each file?
Let's dive into each directory.

#### ExamenesUnicauca:
- **static:** This subdirectory stores all static files like .css, .js or layout images
- **templates:** This subdirectory stores all html files of the project
- **admin.py:** This file register the project's models into the admin app
- **models.py:** This file defines the previously mentioned models of the project
- **tests.py:** This file defines some general test for the app
- **urls.py:** This file defines the urls of the web page and the related functions
- **views.py:** This file defines the functions related to the previously mentioned urls. There is a function for every url created, a function for getting the pagination and the definition of the forms

#### MyWebPage:
- **settings.py:** This file contains the settings of the project. It is set Bogota's time zone and the root for the media files.
- **urls.py:** This file defines the urls of the entire project. By this moment, there's only 2 apps registered (ExamenesUnicauca and the AdminApp)

#### Media:
It's the directory where all image contributions are stored.

#### Manage.py:
It's the main file of the project. It is responsible for running the server.

#### Requirements.txt:
It's the file that specifies the modules and versions that the project requires for working fine.

### How do I run the project?
At first, you need to install all modules used in this project. As long as you have installed django with the specified version of the requirement.txt file, you won't have any issue. However, if this is your first time using django, you can easily go to your project's path in the command prompt and run the next command:
>pip **install** -r **requirements**.**txt**

Then, you should run the following two commands in order to migrate all the models to the database:
>python manage.py **makemigrations** **ExamenesUnicauca**

>python manage.py **migrate**

Now you can run the server by typing this last command:
>python manage.py **runserver**

And that's all. Go to your browser, search for *127.0.0.1* and you should be redirected to the main page of the web.

### Future work
By this moment, the web page only allows students of Electronic Engineering to make their contributions because the mind behind the page is one of them. As long as time passes, it’s expected to meet some interested students who belong to other programs and want to be part of this project. The main idea is having one student out of each program, who will be the super user responsible for the contributions made by students of his program.

It is also a future task to add a section that shows the most popular contributions. The popularity will be based on visits to each contribution and to make this possible, a field called visits has been created and added to the Contribution model. This integer field is increased by one every time an user visits the contribution view page.

Finally, having in mind this repository has been created in order to get reviewed, there are some contributions previously created and a superuser account whose username is “*jhon*” and password is “*jhon*”. Don’t ignore the .sqlite3 file.
