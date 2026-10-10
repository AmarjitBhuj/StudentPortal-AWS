const API_URL =
    "https://zzxgmd8bz8.execute-api.us-east-1.amazonaws.com/students";

const form = document.getElementById("studentForm");
const message = document.getElementById("message");
const studentsList = document.getElementById("studentsList");
const refreshBtn = document.getElementById("refreshBtn");
const studentCount = document.getElementById("studentCount");


/* =========================
   Load Students
========================= */

async function loadStudents() {

    studentsList.innerHTML = `
        <tr>
            <td colspan="5" class="loading">
                Loading students...
            </td>
        </tr>
    `;

    try {

        const response = await fetch(API_URL);

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.message || "Failed to load students"
            );
        }

        /* Update total student count */
        studentCount.textContent = data.students.length;


        /* No students */
        if (data.students.length === 0) {

            studentsList.innerHTML = `
                <tr>
                    <td colspan="5" class="loading">
                        No students found.
                    </td>
                </tr>
            `;

            return;
        }


        /* Clear table */
        studentsList.innerHTML = "";


        /* Add each student as a table row */
        data.students.forEach(student => {

            const row = document.createElement("tr");

            row.innerHTML = `
                <td>${student.id}</td>

                <td>
                    <strong>${student.name}</strong>
                </td>

                <td>
                    ${student.email}
                </td>

                <td>
                    ${student.course || "Not specified"}
                </td>

                <td>
                    ${student.year || "Not specified"}
                </td>
            `;

            studentsList.appendChild(row);

        });

    } catch (error) {

        studentsList.innerHTML = `
            <tr>
                <td colspan="5" class="loading">
                    Unable to load students: ${error.message}
                </td>
            </tr>
        `;

        studentCount.textContent = "-";
    }
}


/* =========================
   Add Student
========================= */

form.addEventListener("submit", async (event) => {

    event.preventDefault();


    const student = {

        name: document.getElementById("name").value.trim(),

        email: document.getElementById("email").value.trim(),

        course: document.getElementById("course").value.trim(),

        year: Number(
            document.getElementById("year").value
        )

    };


    message.textContent = "Adding student...";


    try {

        const response = await fetch(API_URL, {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify(student)

        });


        const data = await response.json();


        if (!response.ok) {

            throw new Error(
                data.message || "Failed to add student"
            );

        }


        message.textContent =
            "Student added successfully!";


        form.reset();


        /* Reload table and count */
        await loadStudents();


    } catch (error) {

        message.textContent =
            `Error: ${error.message}`;

    }

});


/* =========================
   Refresh Button
========================= */

refreshBtn.addEventListener(
    "click",
    loadStudents
);


/* =========================
   Initial Load
========================= */

loadStudents();