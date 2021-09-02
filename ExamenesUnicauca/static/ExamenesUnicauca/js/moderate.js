document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.btn-success').forEach(function(button) {
        button.addEventListener('click', () => success_function(button));
    });
    document.querySelectorAll('.btn-danger').forEach(function(button) {
        button.addEventListener('click', () => elimination_function(button));
    });
    document.querySelectorAll('.btn-secondary').forEach(function(button) {
        button.addEventListener('click', () => edition_function(button));
    });
});

function success_function(button){
    if (confirm("¿Estás seguro que deseas aceptar este aporte?")){
        fetch(`/contribution/${button.dataset.contribution}`, {
            method: 'PUT',
            body: JSON.stringify({
                flag: true
            })
        });
        location.href = `/contribution/${button.dataset.contribution}`;
    }
    else{
    }
}

function elimination_function(button){
    if (confirm("¿Estás seguro que deseas eliminar este aporte?")){
        fetch(`/contribution/${button.dataset.contribution}`, {
            method: 'PUT',
            body: JSON.stringify({
                flag: false
            })
        });
        location.href = '/';
    }
}
