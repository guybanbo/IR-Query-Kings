// Function to populate the header with JSON data
function populateHeader(data) {
  // Update the photo
  document.getElementById("photo").src = data.photo;

  // Update the name
  document.getElementById("name").textContent = data.name;

  // Update the hobbies
  document.getElementById("hobbies").textContent = data.hobbies;

  // Update the courses table
  const coursesTableBody = document
    .getElementById("courses-table")
    .querySelector("tbody");
  coursesTableBody.innerHTML = ""; // Clear existing rows
  data.courses.forEach((course) => {
    const row = document.createElement("tr");
    row.innerHTML = `<td>${course.courseName}</td>`;
    coursesTableBody.appendChild(row);
  });

  // Update the email
  const emailElement = document.getElementById("email");
  emailElement.textContent = data.email;
  emailElement.href = `mailto:${data.email}`;
  
  // Update the header ID with the username
  const newHeaderId = data.name.toLowerCase().replace(/\s+/g, "-");
  document.querySelector("header").id = newHeaderId;

  // Highlight the corresponding nav link
  const navLinks = document.querySelectorAll(".navbar-nav .nav-link");
  navLinks.forEach((link) => {
    // Remove active class from all links
    link.classList.remove("active");
    // Check if the link href matches the updated header ID
    if (link.href.includes(`#${newHeaderId}`)) {
      link.classList.add("active");
    }
  });
}

// Fetch the JSON file and filter for the specific student based on the URL
function loadStudentProfile() {
  // Get the student ID from the URL query parameters
  const urlParams = new URLSearchParams(window.location.search);
  const studentId = parseInt(urlParams.get("id"), 10); // Get the 'id' parameter

  if (!studentId) {
    console.error("Student ID is missing in the URL.");
    return;
  }

  // Fetch the JSON file
  fetch("students.json")
    .then((response) => response.json())
    .then((students) => {
      // Find the student with the matching ID
      const student = students.find((s) => s.id === studentId);

      if (student) {
        // Populate the header with the student's data
        populateHeader(student);
      } else {
        console.error("Student not found.");
      }
    })
    .catch((error) => console.error("Error loading JSON:", error));
}

// Call loadStudentProfile when the page loads
window.onload = loadStudentProfile;

