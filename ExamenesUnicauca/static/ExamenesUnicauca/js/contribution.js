document.addEventListener('DOMContentLoaded', function() {
    // Example starter JavaScript for disabling form submissions if there are invalid fields
    (function () {
        'use strict'
        // Fetch all the forms we want to apply custom Bootstrap validation styles to
        var forms = document.querySelectorAll('.needs-validation')
        // Loop over them and prevent submission
        Array.prototype.slice.call(forms)
        .forEach(function (form) {
            form.addEventListener('submit', function (event) {
                if (!form.checkValidity()) {
                    event.preventDefault()
                    event.stopPropagation()
                }
                form.classList.add('was-validated')
            }, false)
        })
    })();
    // Codigo para mostrar el form escogido
    document.querySelector('#category').addEventListener('change',(event)=>{
        if(event.target.value=='Parcial'){
            document.querySelector('#parcial-form').style.display = 'block';
            document.querySelector('#solution-form').style.display = 'none';
            document.querySelector('#note-form').style.display = 'none';
        }
        else if(event.target.value=='Solucionario'){
            document.querySelector('#solution-form').style.display = 'block';
            document.querySelector('#parcial-form').style.display = 'none';
            document.querySelector('#note-form').style.display = 'none';
        }
        else{
            document.querySelector('#note-form').style.display = 'block';
            document.querySelector('#solution-form').style.display = 'none';
            document.querySelector('#parcial-form').style.display = 'none';
        }
    });
    // Codigo para añadir mas de un campo de imagen y borrarlo
    var aux = 0;       
    document.querySelectorAll('.add-field').forEach((obj)=>{
        obj.addEventListener('click', function(ev){ 
            aux++;
            let imageDiv = ev.target.parentElement.parentElement;
            let newDiv = document.createElement('div');
            newDiv.className = 'col-11';
            newDiv.innerHTML = `
            <div class="form-group custom-file">
                <p class="error_message">{{ form.img.errors }}</p>
                <input type="file" class="custom-file-input customFile${aux}" id="customFile${aux}" required name="img[]" accept="image/*">
                <label class="custom-file-label customFileName${aux}" for="customFile${aux}">Carga una imágen de tu aporte</label>
                <div class="invalid-feedback">Por favor introduzca una imágen válida.</div>
            </div>
            `;
            let newDiv2 = document.createElement('div');
            newDiv2.className = 'col-1';
            newDiv2.innerHTML = `<span class="btn btn-danger remove-field">-</span>`;
    
            let line1 = document.createElement('br');
            let line2 = document.createElement('br');
            imageDiv.appendChild(line1);
            imageDiv.appendChild(line2);
            imageDiv.appendChild(newDiv);
            imageDiv.appendChild(newDiv2);
    
            document.querySelectorAll(`.custom-file-input`).forEach((e)=>{
                e.addEventListener('change', function(){
                    let name = e.files[0].name;
                    e.nextElementSibling.innerHTML = name;
                });
            });
    
            document.querySelectorAll(`.remove-field`).forEach((e)=>{
                e.addEventListener('click', function(){
                    e.parentElement.previousElementSibling.remove();
                    e.parentElement.previousElementSibling.remove();
                    e.parentElement.previousElementSibling.remove();
                    e.parentElement.remove();
                });
            });          
    
        });
    });
    
    document.querySelectorAll(`.customFile0`).forEach(obj=>{
        obj.addEventListener('change', function(){
            let name = obj.files[0].name;
            obj.nextElementSibling.innerHTML = name;
        });
    });
    // Codigo para traer aportes para el dropdown del solucionario
    document.querySelectorAll('.refresh-contributions').forEach(obj=>{
        obj.addEventListener('input', ()=>{
            // Elimina las opciones
            let contribution_of_solution = document.querySelector('#contribution');
            let opciones = contribution_of_solution.querySelectorAll('option');
            for(let i=1; i<opciones.length;i++){
                opciones[i].remove();
            }
            // Carga los aportes
            fetch(`/solutions/`, {
                method: 'POST',
                body: JSON.stringify({
                    career_name : document.querySelector('#career_name').value,
                    teacher_first_name : document.querySelector('#teacher_first_name').value,
                    teacher_last_name : document.querySelector('#teacher_last_name').value,
                    course_name : document.querySelector('#course_name').value
                })
            }).then(response => response.json())
            .then(contributions => {
                contributions.forEach(contribution => {
                    textoNuevaOpcion = `Semestre ${contribution.semester} - ${contribution.course} - ${contribution.teacher} - ${contribution.year}.${contribution.semester_of_year} - ${contribution.part}`;
                    let newOption = document.createElement('option');
                    newOption.innerHTML = textoNuevaOpcion;
                    contribution_of_solution.appendChild(newOption);
                })
            });
        });
    });
    
});
