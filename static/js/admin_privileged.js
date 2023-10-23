/* Definition of functions that are used on call by the event listeners */
const dataTableStudentsOptions = {
    columnDefs: [
        { className: 'centered', targets: [0, 1, 2] },
        { orderable: false, targets: [2] },
        { searchable: false, targets: [2] }
    ],
    pageLength: 10,
    destroy: true,
};

const dataTableGamesOptions = {
    columnDefs: [
        { className: 'centered', targets: [0, 1, 2, 3, 4, 5] },
        { orderable: false, targets: [0, 1, 2] },
        { searchable: false, targets: [0, 1, 2] }
    ],
    pageLength: 10,
    destroy: true,
};

const dataTableLogsOptions = {
    columnDefs: [
        { className: 'centered', targets: [0, 1, 2, 3] },
        { orderable: false, targets: [0, 1, 3] },
        { searchable: false, targets: [0, 1, 2, 3] }
    ],
    pageLength: 10,
    destroy: true,
};

const dataTableUsersOptions = {
    columnDefs: [
        { className: 'centered', targets: [0, 1, 2, 3] },
        { orderable: false, targets: [0, 1, 2] },
        { searchable: false, targets: [0, 1] }
    ],
    pageLength: 10,
    destroy: true,
};

const studentTemplate = (student) => `
    <tr>
        <td>${student.id}</td>
        <td>${student.name}</td>
        <td>
            <button class='btn btn-sm btn-primary'><i class='fa-solid fa-pencil'></i></button>
            <button class='btn btn-sm btn-danger delete-student' data-id='${student.id}'><i class='fa-solid fa-trash-can'></i></button>
        </td>
    </tr>
`;

const gameTemplate = (game) => `
    <tr>
        <td>${game.id}</td>
        <td>${game.name}</td>
        <td>${game.displayName}</td>
        <td>${game.available ? "<i class='fa-solid fa-check' style='color:green;'></i>" : "<i class='fa-solid fa-xmark' style='color:red;'></i>"}</td>
        <td>${game.show ? "<i class='fa-solid fa-check' style='color:green;'></i>" : "<i class 'fa-solid fa-xmark' style='color:red;'></i>"}</td>
        <td>
            <button class='btn btn-sm btn-primary'><i class='fa-solid fa-pencil'></i></button>
            <button class='btn btn-sm btn-danger delete-game' data-id='${game.id}'><i class='fa-solid fa-trash-can'></i></button>
        </td>
    </tr>
`;

const logTemplate = (log) => `
    <tr>
        <td>${log.id}</td>
        <td>${log.user__username}</td>
        <td>${log.actionPerformed}</td>
        <td>${log.time}</td>
    </tr>
`;

const userTemplate = (user) => `
    <tr>
        <td>${user.id}</td>
        <td>${user.username}</td>
        <td>${user.is_admin ? "<i class='fa-solid fa-check' style='color:green;'></i>" : "<i class='fa-solid fa-xmark' style='color:red;'></i>"}</td>
        <td>
            <button class='btn btn-sm btn-primary'><i class='fa-solid fa-pencil'></i></button>
            <button class='btn btn-sm btn-danger delete-user' data-id='${user.id}'><i class='fa-solid fa-trash-can'></i></button>
        </td>
    </tr>
`;

const listStudents = async () => {
    const data = await fetchData("get-students-list");
    populateTable(data.students, document.getElementById("tableBody_students"), studentTemplate);
};

const listGames = async () => {
    const data = await fetchData("get-games-list");
    populateTable(data.games, document.getElementById("tableBody_games"), gameTemplate);
};

const listLogs = async () => {
    const data = await fetchData("get-logs-list");
    populateTable(data.logs, document.getElementById("tableBody_logs"), logTemplate);
};

const listUsers = async () => {
    const data = await fetchData("get-users-list");
    populateTable(data.users, document.getElementById("tableBody_users"), userTemplate);
};

// Inits all datatables
const initDataTablesPrivileged = async () => {
    await initDataTable("students-table", dataTableStudentsOptions, listStudents);
    await initDataTable("games-table", dataTableGamesOptions, listGames);
    await initDataTable("logs-table", dataTableLogsOptions, listLogs);
    await initDataTable("users-table", dataTableUsersOptions, listUsers);
}

// On page load
window.addEventListener('load', async () => {
    await initDataTablesPrivileged();
    // Modal, set values when editing
    var exampleModal = document.getElementById('exampleModal')
    exampleModal.addEventListener('show.bs.modal', function () { })

    // Game creation form
    $('#submitGame').click(function () {
        // Get form data
        var formData = $('#gameForm').serialize();

        // Send data using AJAX
        $.ajax({
            type: 'POST',
            url: BASEURL + '/api/game',
            data: formData,
            success: function (data) {
                //console.log(data);
                $('#exampleModal').modal('hide');

                // Reload the page to reflect the changes
                location.reload();
            },
            error: function (error) {
                // Handle errors
                console.error(error);
            }
        });
    });

    // User creation form
    $('#submitUser').click(function () {
        // Get form data
        var formData = $('#userForm').serialize();

        // Use regex to check if email is valid
        var email = $('#email').val();
        var emailRegex = /\S+@\S+\.\S+/;
        if (!emailRegex.test(email)) {
            alert("El email no es válido");
            return;
        }
        // Make email before the @ uppercase and add it to formData
        var parts = email.split('@');
        parts[0] = parts[0].toUpperCase();
        // Add to formData the username as the value of the email before the @ with capital letters
        formData += "&username=" + parts[0];
        // Add to formData the email with the username in uppercase
        var modifiedEmail = parts.join('@');
        $('#email').val(modifiedEmail);
        formData += "&email=" + modifiedEmail;

        // Check if passwords aren't empty & match
        var password = $('#password').val();
        var passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$/;
        if (!passwordRegex.test(password)) {
            alert("La contraseña debe tener al menos 8 caracteres, una mayúscula, una minúscula y un número");
            return;
        }

        var password2 = $('#password2').val();
        if (password != password2) {
            alert("Las contraseñas no coinciden");
            return;
        }

        // Send data using AJAX
        $.ajax({
            type: 'POST',
            url: BASEURL + '/api/user',
            data: formData,
            success: function (data) {
                //console.log(data);
                $('#userModal').modal('hide');

                // Reload the page to reflect the changes
                location.reload();
            },
            error: function (error) {
                // Handle errors
                console.error(error);
            }
        });
    });
});

// Student deletion
$(document).on('click', '.delete-student', function () {
    const studentId = $(this).data('id');
    const message = '¿Seguro que quieres borrar este estudiante?';
    confirmAndDelete('student', studentId, message);
});

// Game deletion
$(document).on('click', '.delete-game', function () {
    const gameId = $(this).data('id');
    const message = '¿Seguro que quieres borrar este juego?';
    confirmAndDelete('game', gameId, message);
});

// User deletion
$(document).on('click', '.delete-user', function () {
    const userId = $(this).data('id');
    const message = '¿Seguro que quieres eliminar el acceso a este usuario?';
    confirmAndDelete('user', userId, message);
});