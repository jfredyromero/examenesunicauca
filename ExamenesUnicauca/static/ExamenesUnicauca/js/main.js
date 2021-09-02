document.addEventListener('DOMContentLoaded', ()=>{
        // Para desplegar menu lateral
    const sidePanel = document.querySelector('#side-menu');
    const emptyPanel = document.querySelector('#empty-panel');
    const nav = document.querySelector('#hamburger');
    nav.addEventListener('click', () =>{
        nav.classList.toggle('open');
        sidePanel.classList.toggle('open');
        emptyPanel.classList.toggle('open');
    })

    emptyPanel.addEventListener('click',()=>{
        nav.classList.toggle('open');
        sidePanel.classList.toggle('open');
        emptyPanel.classList.toggle('open');
    })

    // Para desplegar subopciones
    document.querySelectorAll('.list-item').forEach(e=>{
        e.addEventListener('click', event=>{
            event.target.querySelectorAll('.sublist-item').forEach(o=>{
                o.classList.toggle('open');
            })
        })
    })
})