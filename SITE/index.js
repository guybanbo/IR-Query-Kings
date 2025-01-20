// Function to generate the team cards dynamically (for homepage)
function populateTeamCards(students) {
  const teamContainer = document.getElementById("team-members");
  teamContainer.innerHTML = ""; // Clear any existing content

  // Loop through each student and create their card
  students.forEach((student) => {
    const card = document.createElement("div");
    card.classList.add("col-6", "col-lg-3", "mb-5");

    const cardLink = document.createElement("a");
    cardLink.href = `profile.html?id=${student.id}`;

    const portfolioItem = document.createElement("div");
    portfolioItem.classList.add("portfolio-item", "mx-auto");

    const studentPhoto = document.createElement("img");
    studentPhoto.src = student.photo; // Assuming "photo" field contains the URL or file path to the image
    studentPhoto.alt = student.name;
    studentPhoto.classList.add("img-fluid"); // Add Bootstrap styling or customize as needed

    const caption = document.createElement("div");
    caption.classList.add(
      "portfolio-item-caption",
      "d-flex",
      "align-items-center",
      "justify-content-center",
      "h-100",
      "w-100"
    );

    const captionContent = document.createElement("div");
    captionContent.classList.add(
      "portfolio-item-caption-content",
      "text-center",
      "text-white"
    );
    captionContent.textContent = student.name;

    // Append the caption to the portfolio item
    caption.appendChild(captionContent);
        portfolioItem.appendChild(studentPhoto);

    portfolioItem.appendChild(caption);

    // Append the portfolio item to the card link
    cardLink.appendChild(portfolioItem);

    // Append the card link to the card div
    card.appendChild(cardLink);

    // Append the card to the container
    teamContainer.appendChild(card);
  });
}

// Fetch the student data and populate the team section
fetch("students.json")
  .then((response) => response.json())
  .then((students) => populateTeamCards(students))
  .catch((error) => console.error("Error loading student data:", error));
