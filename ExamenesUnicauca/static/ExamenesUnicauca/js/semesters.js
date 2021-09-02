document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.btn-semester').forEach(function(button) {
        button.addEventListener('click', () => show_courses(button));
    });
});

function show_courses(button){
    const career = document.querySelector('h2').innerHTML;
    document.querySelector('#courses').innerHTML = '';
    document.querySelector('#teachers').innerHTML = '';
    fetch(`${career}/${button.dataset.semester}`)
    .then(response => response.json())
    .then(courses => {
        if(courses.length>0){
            courses.forEach(course => {
                const course_div = button.cloneNode(true);
                course_div.innerHTML = `<h4>${course.name}</h4>
                <span class="badge badge-info badge-pill"><h5>${course.teachers.length}</h5></span>`;
                course_div.class = "courses";
                course_div.addEventListener('click', () => show_teachers_of_course(course, button));
                document.querySelector('#courses').append(course_div);
                window.location.hash = '.courses';
            })
            document.querySelector('#semesters').parentElement.classList.toggle('semesters-container');
            document.querySelector('#courses').parentElement.classList.toggle('courses-container');
        }
    });
}

function show_teachers_of_course(course, button){
    document.querySelector('#teachers').innerHTML = '';
    let aux = 0;
    if(course.teachers.length>0){
        course.teachers.forEach(teacher => {
            const teacher_div = button.cloneNode(true);
            teacher_div.innerHTML = `<h4>${teacher}</h4>
            <span class="badge badge-info badge-pill"><h5>${course.contributions_of_teachers[aux]}</h5></span>`;
            aux++;
            teacher_div.class = "teachers";
            teacher_div.addEventListener('click', () => show_contributions_of_teacher(course.name, teacher));
            document.querySelector('#teachers').append(teacher_div);
            window.location.hash = '.teachers';
        })
        document.querySelector('#courses').parentElement.classList.toggle('courses-container');
        document.querySelector('#teachers').parentElement.classList.toggle('teachers-container');
    }
}

function show_contributions_of_teacher(course_name, teacher){
      location.href = `/course/${course_name}/${teacher}`;
}
