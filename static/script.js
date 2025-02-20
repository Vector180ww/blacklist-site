document.getElementById('employeeForm').addEventListener('submit', function(e) {
    e.preventDefault();

    const formData = new FormData();
    formData.append('name', document.getElementById('name').value);
    formData.append('reason', document.getElementById('reason').value);
    formData.append('photo', document.getElementById('photo').files[0]);

    fetch('/add_employee', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            loadEmployees();
            this.reset();
        }
    })
    .catch(error => console.error('Ошибка:', error));
});

function displayEmployee(id, name, reason, photoUrl) {
    const list = document.getElementById('employeeList');
    const item = document.createElement('li');
    item.classList.add('employee-item');
    item.dataset.id = id;  // Сохраняем ID сотрудника

    item.innerHTML = `
        <div>
            <strong>${name}</strong><br>
            ${reason}
        </div>
    `;
    if (photoUrl) {
        const img = document.createElement('img');
        img.src = photoUrl;
        item.appendChild(img);
    }

    // Добавляем кнопку удаления
    const deleteButton = document.createElement('button');
    deleteButton.textContent = 'Удалить';
    deleteButton.onclick = function() {
        fetch(`/delete_employee/${id}`, {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'deleted') {
                loadEmployees();
            }
        })
        .catch(error => console.error('Ошибка удаления:', error));
    };
    item.appendChild(deleteButton);

    list.appendChild(item);
}

document.getElementById('searchInput').addEventListener('input', function() {
    const searchTerm = this.value.toLowerCase();
    const items = document.querySelectorAll('.employee-item');

    items.forEach(item => {
        const name = item.querySelector('strong').textContent.toLowerCase();
        item.style.display = name.includes(searchTerm) ? 'flex' : 'none';
    });
});

function loadEmployees() {
    fetch('/get_employees')
    .then(response => response.json())
    .then(employees => {
        document.getElementById('employeeList').innerHTML = '';
        employees.forEach(emp => displayEmployee(emp.id, emp.name, emp.reason, emp.photo));
    })
    .catch(error => console.error('Ошибка:', error));
}

loadEmployees();