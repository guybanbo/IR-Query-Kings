let sheetData = []; // Store the parsed Excel data
let currentPage = 1; // Current page number
const rowsPerPage = 10; // Number of rows per page
let headerRow = []; // Store the header row

// Fetch and parse the Excel file
fetch("data/tf-idf.xlsx") // Adjust the path if needed
  .then((response) => {
    if (!response.ok) throw new Error("Failed to fetch the Excel file");
    return response.arrayBuffer();
  })
  .then((data) => {
    const workbook = XLSX.read(data, { type: "array" });
    const sheetName = workbook.SheetNames[0];
    const sheet = workbook.Sheets[sheetName];
    sheetData = XLSX.utils.sheet_to_json(sheet, { header: 1 });

    // Separate the header row and remaining data
    headerRow = sheetData.shift(); // Remove the first row and store it as the header
    console.log(sheetData);
    renderPage(); // Render the first page
  })
  .catch((error) => console.error("Error loading Excel file:", error));

// Render the current page
function renderPage() {
  const table = document.getElementById("excelTable");
  table.innerHTML = ""; // Clear previous table data

  // Render header row
  const thead = document.createElement("thead");
  const headerRowElement = document.createElement("tr");
  headerRow.forEach((header) => {
    const th = document.createElement("th");
    th.textContent = header || ""; // Handle empty cells
    headerRowElement.appendChild(th);
  });
  thead.appendChild(headerRowElement);
  table.appendChild(thead);

  // Render current page data
  const tbody = document.createElement("tbody");
  const start = (currentPage - 1) * rowsPerPage;
  const end = start + rowsPerPage;
  const pageData = sheetData.slice(start, end);

  pageData.forEach((row) => {
    const rowElement = document.createElement("tr");
    row.forEach((cell) => {
      const cellElement = document.createElement("td");
      cellElement.textContent = cell || 0; // Handle empty cells
      
      rowElement.appendChild(cellElement);
    });
    tbody.appendChild(rowElement);
  });
  table.appendChild(tbody);

  // Update pagination info
  const totalPages = Math.ceil(sheetData.length / rowsPerPage);
  document.getElementById(
    "pageInfo"
  ).textContent = `Page ${currentPage} of ${totalPages}`;

  // Disable buttons when necessary
  document.getElementById("prevPage").disabled = currentPage === 1;
  document.getElementById("nextPage").disabled = currentPage === totalPages;
}

// Event listeners for pagination buttons
document.getElementById("prevPage").addEventListener("click", () => {
  if (currentPage > 1) {
    currentPage--;
    renderPage();
  }
});

document.getElementById("nextPage").addEventListener("click", () => {
  if (currentPage < Math.ceil(sheetData.length / rowsPerPage)) {
    currentPage++;
    renderPage();
  }
});


/**
 * 
 * 
 *  Interactive Acronym Finder                           
 *                               
 * 
 */

let excelData = []; // Store the parsed Excel data

// Fetch and parse the Excel file
fetch("data/q3.xlsx") // Replace with your file path
  .then((response) => {
    if (!response.ok) throw new Error("Failed to fetch the Excel file");
    return response.arrayBuffer();
  })
  .then((data) => {
    const workbook = XLSX.read(data, { type: "array" });
    const sheetName = workbook.SheetNames[0];
    const sheet = workbook.Sheets[sheetName];
    excelData = XLSX.utils.sheet_to_json(sheet);

    populateCategories(); // Populate the categories dropdown
  })
  .catch((error) => console.error("Error loading Excel file:", error));

// Populate categories in the dropdown
function populateCategories() {
  const categorySelect = document.getElementById("categorySelect");
  const categorySet = new Set(); // Use a Set to avoid duplicates

  // Loop through rows and split categories by commas
  excelData.forEach((row) => {
    if (row.Category) {
      const categories = row.Category.split(",").map((cat) => cat.trim()); // Split and trim spaces
      categories.forEach((category) => categorySet.add(category)); // Add each category to the Set
    }
  });

  // Convert Set to Array and sort alphabetically
  const sortedCategories = Array.from(categorySet).sort();

  // Populate the category dropdown
  sortedCategories.forEach((category) => {
    const option = document.createElement("option");
    option.value = category;
    option.textContent = category;
    categorySelect.appendChild(option);
  });

  categorySelect.addEventListener("change", populateAcronyms);
}

// Populate acronyms based on the selected category
function populateAcronyms() {
  const categorySelect = document.getElementById("categorySelect");
  const acronymSelect = document.getElementById("acronymSelect");
  acronymSelect.innerHTML = '<option value="">-- Select Acronym --</option>'; // Clear previous options

  const selectedCategory = categorySelect.value;
  const acronyms = [
    ...new Set(
      excelData
        .filter(
          (row) =>
            row.Category &&
            row.Category.split(",")
              .map((cat) => cat.trim())
              .includes(selectedCategory)
        ) // Match category
        .map((row) => row.Acronym)
    ),
  ]; // Unique acronyms in the selected category

  acronyms.forEach((acronym) => {
    const option = document.createElement("option");
    option.value = acronym;
    option.textContent = acronym;
    acronymSelect.appendChild(option);
  });

  acronymSelect.addEventListener("change", displayDefinitions);
}

// Display definitions based on the selected acronym
function displayDefinitions() {
  const acronymSelect = document.getElementById("acronymSelect");
  const definitionTable = document.getElementById("definitionTable");
  const tbody = definitionTable.querySelector("tbody");
  tbody.innerHTML = ""; // Clear previous data

  const selectedAcronym = acronymSelect.value;
  const rows = excelData.filter((row) => row.Acronym === selectedAcronym);

  rows.forEach((row) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${row.Acronym}</td>
      <td>${row.Definition}</td>
      <td>${row.Category}</td>
      <td>${row.Page}</td>
      <td><a href="${row.Link}" target="_blank">Link</a></td>
    `;
    tbody.appendChild(tr);
  });

  definitionTable.style.display = rows.length > 0 ? "table" : "none"; // Show table if rows exist
}
