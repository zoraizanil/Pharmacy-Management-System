// ✅ Toggle Sidebar
function toggleSidebar() {
  const sidebar = document.getElementById("sidebar");
  sidebar.classList.toggle("collapsed");
}

// ✅ Toggle Submenu (Generic One)
function toggleSubmenu(id, element) {
  const submenus = document.querySelectorAll(".nav > li > ul");
  const icons = document.querySelectorAll(".nav-link i.bi-caret-right-fill");

  submenus.forEach((menu) => {
    if (menu.id !== id) menu.classList.add("d-none");
  });

  icons.forEach((icon) => icon.classList.remove("rotate-down"));

  const submenu = document.getElementById(id);
  submenu.classList.toggle("d-none");

  if (!submenu.classList.contains("d-none")) {
    const icon = element.querySelector("i.bi-caret-right-fill");
    if (icon) icon.classList.add("rotate-down");
  }
}

function setActiveNavLink(clickedLink) {
  document.querySelectorAll("#sidebar .nav-link").forEach((link) => {
    link.classList.remove("active");
  });
  clickedLink.classList.add("active");
}

// ✅ Load Page via AJAX
function loadPage(url) {
  console.log('🔍 THIS IS THE UPDATED LOADPAGE FUNCTION 🔍');
  console.log('=== loadPage called with URL:', url, '===');
  fetch(url)
    .then((response) => {
      if (!response.ok) throw new Error("Page not found");
      return response.text();
    })
    .then((html) => {
      console.log('HTML loaded, injecting into content-area');
      const contentArea = document.getElementById("content-area");
      const parser = new DOMParser();
      const doc = parser.parseFromString(html, 'text/html');
      
      // Replace content
      contentArea.innerHTML = doc.body.innerHTML;

      // Execute scripts
      Array.from(doc.body.querySelectorAll('script')).forEach(oldScript => {
        const newScript = document.createElement('script');
        Array.from(oldScript.attributes).forEach(attr => {
            newScript.setAttribute(attr.name, attr.value);
        });
        newScript.appendChild(document.createTextNode(oldScript.innerHTML));
        contentArea.appendChild(newScript);
      });

      initPharmacyDropdowns();
      initPharmacyForm();
      initDeleteForms();
      initCreateManagerForm();
      initCreateStaffForm();
      initCreateAdminForm();
      initInventoryPage();
      console.log('Checking URL for special pages...');
      if (url.includes('see-inventory')) {
        console.log('Detected see-inventory page, calling initSeeInventoryPage');
        initSeeInventoryPage();
      }
      if (url.includes('managers')) {
        console.log('Detected managers page, calling fetchManagersData');
        fetchManagersData();
      }
      if (url.includes('staff')) {
        console.log('Detected staff page, calling fetchStaffData');
        fetchStaffData();
      }
      console.log('=== loadPage completed ===');
    })
    .catch((error) => {
      console.error('loadPage error:', error);
      document.getElementById("content-area").innerHTML =
        "<h3>Page not found.</h3>";
    });
}

// ✅ Add-Pharmacy-Form-Submission
function initPharmacyForm() {
  const submitBtn = document.getElementById("submitBtn");
  if (!submitBtn) return;

  submitBtn.addEventListener("click", function () {
    const csrfToken = document.querySelector(
      "[name=csrfmiddlewaretoken]"
    ).value;
    const name = document.getElementById("pharmacyName").value;
    const location = document.getElementById("pharmacyAddress").value;

    fetch("/pharmacy/add-pharmacy/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      },
      body: JSON.stringify({ name, location }),
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.success) {
          alert("Pharmacy saved successfully!");
          document.getElementById("addPharmacyForm").reset();
        } else {
          alert("Error: " + (data.error || "Unable to save."));
        }
      })
      .catch(() => alert("Something went wrong."));
  });
}

// ✅ Delete-Pharmacy-Form-Submission
function initDeleteForms() {
  document.querySelectorAll(".delete-form").forEach((form) => {
    form.addEventListener("submit", function (e) {
      e.preventDefault();

      if (!confirm("Are you sure you want to delete this pharmacy?")) return;

      const pharmacyId = form.querySelector("[name='pharmacy_id']").value;
      const csrfToken = form.querySelector(
        "[name='csrfmiddlewaretoken']"
      ).value;

      fetch("/pharmacy/delete/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify({ pharmacy_id: pharmacyId }),
      })
        .then((res) => res.json())
        .then((data) => {
          if (data.success) {
            const ids = pharmacyId.split(",").map((id) => id.trim());
            ids.forEach((id) => {
              const row = document.getElementById(`pharmacy-row-${id}`);
              if (row) row.remove();
              selectedPharmacyIds.delete(parseInt(id));
            });

            document.getElementById("pharmacy_id").value = "";
            document.getElementById("deleteButton").disabled = true;

            alert("Pharmacy deleted successfully.");
          } else {
            alert("Failed to delete: " + data.error);
          }
        })
        .catch(() => {
          alert("Something went wrong. Please try again.");
        });
    });
  });
}

// select pharmacies in delete-pharmacy table
let selectedPharmacyIds = new Set();
function selectPharmacy(id, forceSelect = null) {
  const row = document.getElementById("pharmacy-row-" + id);
  const checkbox = row.querySelector(".pharmacy-checkbox");
  const shouldSelect =
    forceSelect !== null ? forceSelect : !selectedPharmacyIds.has(id);

  if (shouldSelect) {
    selectedPharmacyIds.add(id);
    checkbox.checked = true;
  } else {
    selectedPharmacyIds.delete(id);
    checkbox.checked = false;
    row.style.backgroundColor = "";
  }

  document.getElementById("pharmacy_id").value =
    Array.from(selectedPharmacyIds).join(",");
  document.getElementById("deleteButton").disabled =
    selectedPharmacyIds.size === 0;

  const all = document.querySelectorAll(".pharmacy-checkbox").length;
  const selected = selectedPharmacyIds.size;
  const checkAll = document.getElementById("checkAll");
  if (checkAll) checkAll.checked = selected === all;
}

function onRowClick(id, event) {
  if (event.target.tagName.toLowerCase() === "input") return;
  selectPharmacy(id);
}

function onCheckboxClick(id, event) {
  event.stopPropagation();
  selectPharmacy(id);
}

function onCheckAllClick() {
  const checkAll = document.getElementById("checkAll");
  const isChecked = checkAll.checked;
  const checkboxes = document.querySelectorAll(".pharmacy-checkbox");

  checkboxes.forEach((cb) => {
    const id = parseInt(cb.value);
    selectPharmacy(id, isChecked);
  });
}

// ✅ Dropdown Logic
function initPharmacyDropdowns() {
  const dropdownConfigs = [
    {
      buttonSelector: "#manager-form .dropdown-toggle",
      menuSelector: "#manager-Dropdown",
      inputType: "checkbox",
      placeholder: "Select Pharmacy",
    },
    {
      buttonSelector: "#staff-form .dropdown-toggle",
      menuSelector: "#staff-Dropdown",
      inputType: "radio",
      placeholder: "Select Pharmacy",
    },
  ];

  dropdownConfigs.forEach((config) => {
    const dropdownButton = document.querySelector(config.buttonSelector);
    const dropdownMenu = document.querySelector(config.menuSelector);

    if (!dropdownButton || !dropdownMenu) return;

    let pharmaciesLoaded = false;

    dropdownButton.addEventListener("click", () => {
      if (pharmaciesLoaded) return;

      fetch("/pharmacy/api/pharmacies/")
        .then((response) => response.json())
        .then((result) => {
          dropdownMenu.innerHTML = "";

          if (!result.success || !result.pharmacies || result.pharmacies.length === 0) {
            dropdownMenu.innerHTML = "<li>No pharmacies found</li>";
            return;
          }

          result.pharmacies.forEach((pharmacy) => {
            const item = document.createElement("li");
            item.innerHTML = `
              <label>
                <input type="${config.inputType}" name="${
              config.inputType === "radio" ? "assigned_pharmacy" : "pharmacies"
            }" value="${pharmacy.id}" id="pharmacy-${pharmacy.id}">
                ${pharmacy.name}
              </label>
            `;
            dropdownMenu.appendChild(item);
          });

          dropdownMenu.addEventListener("click", (e) => e.stopPropagation());

          dropdownMenu.addEventListener("change", () => {
            let selectedLabels = [];

            if (config.inputType === "checkbox") {
              selectedLabels = Array.from(
                dropdownMenu.querySelectorAll("input[type='checkbox']:checked")
              ).map((input) => input.parentElement.textContent.trim());
            } else {
              const selectedRadio = dropdownMenu.querySelector(
                "input[type='radio']:checked"
              );
              selectedLabels = selectedRadio
                ? [selectedRadio.parentElement.textContent.trim()]
                : [];
            }

            dropdownButton.textContent = selectedLabels.length
              ? selectedLabels.join(", ")
              : config.placeholder;
          });

          pharmaciesLoaded = true;
        })
        .catch((error) => {
          console.error("Error fetching pharmacies:", error);
        });
    });
  });
}

// eye button in password field
function togglePassword(inputId, icon) {
  const input = document.getElementById(inputId);
  if (input.type === "password") {
    input.type = "text";
    icon.classList.remove("bi-eye-slash");
    icon.classList.add("bi-eye");
  } else {
    input.type = "password";
    icon.classList.remove("bi-eye");
    icon.classList.add("bi-eye-slash");
  }
}

function handleInput(input, iconId) {
  const icon = document.getElementById(iconId);
  icon.style.display = input.value.length > 0 ? "block" : "none";
}

document.addEventListener("DOMContentLoaded", function () {
  document.addEventListener("click", function (e) {
    const password1Elem = document.getElementById("password1");
    const password2Elem = document.getElementById("password2");
    const errorMsg = document.getElementById("password-error");

    // Null check to avoid errors
    if (!password1Elem || !password2Elem || !errorMsg) return;

    const password1 = password1Elem.value;
    const password2 = password2Elem.value;

    if (password1 && password2) {
      if (password1 !== password2) {
        errorMsg.style.display = "block";
      } else {
        errorMsg.style.display = "none";
      }
    } else {
      errorMsg.style.display = "none";
    }
  });
});

// ✅ Create-Manager-Form-Submission
function initCreateManagerForm() {
  const submitBtn = document.getElementById("submitBtn");
  const form = document.getElementById("createManagerForm");
  if (!submitBtn || !form) return;

  submitBtn.addEventListener("click", function (e) {
    e.preventDefault();

    const selectedPharmacies = document.querySelectorAll(
      'input[name="pharmacies"]:checked'
    );

    if (selectedPharmacies.length === 0) {
      alert("At-Least 1 Pharmacy must be Added");
      return;
    }

    const csrfToken = document.querySelector(
      "[name=csrfmiddlewaretoken]"
    ).value;

    const postData = {
      username: form.querySelector('[name="username"]').value,
      first_name: form.querySelector('[name="first_name"]').value,
      last_name: form.querySelector('[name="last_name"]').value,
      email: form.querySelector('[name="email"]').value,
      password1: form.querySelector('[name="password1"]').value,
      password2: form.querySelector('[name="password2"]').value,
      pharmacies: Array.from(selectedPharmacies).map((cb) => cb.value),
    };

    fetch("/create-manager/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      },
      body: JSON.stringify(postData),
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.success) {
          alert("Manager created successfully!");
          form.reset();
        } else {
          alert("Error: " + (data.error || "Could not create manager."));
        }
      })
      .catch(() => alert("Something went wrong."));
  });
}

// ✅ Create-Staff-Form-Submission
function initCreateStaffForm() {
  const submitBtn = document.getElementById("submitStaffBtn");
  const form = document.getElementById("createStaffForm");
  if (!submitBtn || !form) return;

  submitBtn.addEventListener("click", function (e) {
    e.preventDefault();

    const selectedPharmacy = form.querySelector(
      'input[name="assigned_pharmacy"]:checked'
    );

    if (!selectedPharmacy) {
      alert("A pharmacy must be assigned to the staff member.");
      return;
    }

    const csrfToken = document.querySelector(
      "[name=csrfmiddlewaretoken]"
    ).value;

    const postData = {
      username: form.username.value,
      first_name: form.first_name.value,
      last_name: form.last_name.value,
      email: form.email.value,
      password1: form.password1.value,
      password2: form.password2.value,
      assigned_pharmacy: selectedPharmacy.value,
    };

    fetch("/create-staff/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      },
      body: JSON.stringify(postData),
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.success) {
          alert("Staff created successfully!");
          form.reset();
          // Also reset the dropdown button text
          const dropdownButton = document.querySelector("#staff-form .dropdown-toggle");
          if(dropdownButton) dropdownButton.textContent = "Select Pharmacy";
        } else {
          alert("Error: " + (JSON.stringify(data.errors) || data.error || "Could not create staff."));
        }
      })
      .catch(() => alert("Something went wrong."));
  });
}

// ✅ Create-Admin-Form-Submission
function initCreateAdminForm() {
  const submitBtn = document.getElementById("submitAdminBtn");
  const form = document.getElementById("createAdminForm");
  if (!submitBtn || !form) return;

  submitBtn.addEventListener("click", function (e) {
    e.preventDefault();

    const csrfToken = document.querySelector(
      "[name=csrfmiddlewaretoken]"
    ).value;

    const postData = {
      username: form.username.value,
      first_name: form.first_name.value,
      last_name: form.last_name.value,
      email: form.email.value,
      password1: form.password1.value,
      password2: form.password2.value,
    };

    fetch("/create-admin/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      },
      body: JSON.stringify(postData),
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.success) {
          alert("Admin created successfully!");
          form.reset();
        } else {
          alert("Error: " + (data.error || "Could not create admin."));
        }
      })
      .catch(() => alert("Something went wrong."));
  });
}

// Inventory-page-javascript
function initInventoryPage() {
  const pharmacyDropdown = document.getElementById("pharmacy-dropdown");
  const locationDropdown = document.getElementById("location-select");
  const pharmacyIdInput = document.getElementById("pharmacy-id");
  const pharmacyNameInput = document.getElementById("pharmacy-name");

  if (!pharmacyDropdown || !locationDropdown) return;

  locationDropdown.classList.add("hidden");

  fetch("/inventory/api/pharmacies/")
    .then((response) => response.json())
    .then((result) => {
      if(result.success && result.pharmacies) {
        pharmacyDropdown.innerHTML =
          "<option selected disabled>Select Pharmacy</option>";

        result.pharmacies.forEach((pharmacy) => {
          const option = document.createElement("option");
          option.value = pharmacy.id;
          option.textContent = pharmacy.name;
          option.dataset.name = pharmacy.name;
          option.dataset.location = pharmacy.location;
          pharmacyDropdown.appendChild(option);
        });
      }
    })
    .catch((error) => {
      console.error("Error loading pharmacies:", error);
    });

  pharmacyDropdown.addEventListener("change", function () {
    const selectedOption = this.options[this.selectedIndex];
    const location = selectedOption.dataset.location;
    const name = selectedOption.dataset.name;
    const id = selectedOption.value;

    if (location) {
      locationDropdown.innerHTML = "";
      const option = document.createElement("option");
      option.textContent = location;
      option.value = "selected-location";
      locationDropdown.appendChild(option);
      locationDropdown.classList.remove("hidden");
    } else {
      locationDropdown.classList.add("hidden");
    }

    pharmacyIdInput.value = id;
    pharmacyNameInput.value = name;
  });

  document.getElementById("uploadForm").addEventListener("submit", function (e) {
    e.preventDefault();
    const form = e.target;
    const formData = new FormData(form);

    fetch("/inventory/upload-inventory-excel/", {
      method: "POST",
      headers: {
        "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
      },
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        alert(data.message || "Upload complete");
        console.log(data);
      })
      .catch((error) => {
        console.error("Upload failed:", error);
        alert("Error uploading file.");
      });
  });

  initFileInputBrowse();
}

function initFileInputBrowse() {
  const fileInput = document.getElementById("file-input");
  const fileName = document.getElementById("file-name");
  const browseBtn = document.getElementById("browse-btn");

  if (!fileInput || !browseBtn || !fileName) return;

  browseBtn.addEventListener("click", function () {
    fileInput.click();
  });

  fileInput.addEventListener("change", function () {
    if (fileInput.files.length > 0) {
      fileName.value = fileInput.files[0].name;
    }
  });
}

function initSeeInventoryPage() {
    const dropdown = document.getElementById('pharmacy-dropdown');
    const tableContainer = document.getElementById('inventory-table-container');
    const tableBody = document.getElementById('inventory-table-body');
    const noInventoryMsg = document.getElementById('no-inventory-message');
    const pharmacyIdInput = document.getElementById('pharmacy-id');
    const pharmacyNameInput = document.getElementById('pharmacy-name');
    const locationSelect = document.getElementById('location-select');

    if (!dropdown || !tableContainer || !tableBody) return;

    fetch('/inventory/api/pharmacies/')
        .then(response => response.json())
        .then(result => {
            if(result.success && result.pharmacies) {
              dropdown.innerHTML = '<option value="" selected>All Assigned Pharmacies</option>';
              result.pharmacies.forEach(pharmacy => {
                  const option = document.createElement('option');
                  option.value = pharmacy.id;
                  option.textContent = pharmacy.name;
                  option.dataset.name = pharmacy.name;
                  option.dataset.location = pharmacy.location;
                  dropdown.appendChild(option);
              });
            }
        });

    function fetchAndRenderInventory(pharmacyId = "") {
        let url = '/inventory/api/inventory/';
        if (pharmacyId) {
            url += `?pharmacy_id=${pharmacyId}`;
        }
        fetch(url)
            .then(response => response.json())
            .then(data => {
                tableBody.innerHTML = '';
                if (data.success && data.data.length > 0) {
                    data.data.forEach(item => {
                        const row = `<tr>
                            <td>${item.prd_code}</td>
                            <td>${item.name}</td>
                            <td>${item.pharmacy_name}</td>
                            <td>${item.location}</td>
                            <td>${item.qty}</td>
                            <td>${item.price}</td>
                            <td>${item.manufacturedate || ''}</td>
                            <td>${item.expirydate || ''}</td>
                        </tr>`;
                        tableBody.innerHTML += row;
                    });
                    tableContainer.style.display = '';
                    noInventoryMsg.style.display = 'none';
                } else {
                    tableContainer.style.display = 'none';
                    noInventoryMsg.style.display = '';
                }
            });
    }

    fetchAndRenderInventory();

    dropdown.addEventListener('change', function () {
        const selectedOption = this.options[this.selectedIndex];
        const pharmacyId = this.value;
        const pharmacyName = selectedOption.dataset ? selectedOption.dataset.name : '';
        const pharmacyLocation = selectedOption.dataset ? selectedOption.dataset.location : '';

        pharmacyIdInput.value = pharmacyId;
        pharmacyNameInput.value = pharmacyName;

        if (pharmacyId) {
            locationSelect.innerHTML = '';
            locationSelect.disabled = false;
            locationSelect.classList.remove('hidden');
            const locationOption = document.createElement('option');
            locationOption.value = pharmacyLocation;
            locationOption.textContent = pharmacyLocation;
            locationSelect.appendChild(locationOption);
        } else {
            locationSelect.innerHTML = '';
            locationSelect.disabled = true;
            locationSelect.classList.add('hidden');
        }

        fetchAndRenderInventory(pharmacyId);
    });
}

function fetchManagersData() {
  console.log('fetchManagersData called - fetching managers data...');
  
  // Check if table element exists
  const tableBody = document.getElementById('managers-table-body');
  console.log('Table body element found:', !!tableBody);
  if (tableBody) {
    console.log('Table body HTML before fetch:', tableBody.innerHTML);
  }
  
  fetch('/roles/api/managers/')
    .then(response => {
      console.log('Response status:', response.status);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    })
    .then(data => {
      console.log('Managers data received:', data);
      // Render your managers table here
      const tableBody = document.getElementById('managers-table-body');
      if (tableBody) {
        if (data && data.length > 0) {
          tableBody.innerHTML = data.map(manager => `
            <tr>
              <td>${manager.manager_name || ''}</td>
              <td>${manager.date_joined ? new Date(manager.date_joined).toLocaleDateString() : ''}</td>
              <td>${manager.email || ''}</td>
              <td>${manager.name || ''}</td>
              <td>${manager.location || ''}</td>
            </tr>
          `).join('');
          console.log('Table populated with', data.length, 'managers');
          console.log('Table body HTML after population:', tableBody.innerHTML);
        } else {
          tableBody.innerHTML = '<tr><td colspan="5" class="text-center">No managers found</td></tr>';
          console.log('No managers found');
        }
      } else {
        console.error('Table body element not found');
      }
    })
    .catch(error => {
      console.error('Error loading managers:', error);
      const tableBody = document.getElementById('managers-table-body');
      if (tableBody) {
        tableBody.innerHTML = '<tr><td colspan="5" class="text-center text-danger">Error loading managers: ' + error.message + '</td></tr>';
      }
    });
}

function fetchStaffData() {
  const staffTableBody = document.getElementById("staff-table-body");
  const staffTableHead = document.getElementById("staff-table-head");

  console.log('fetchStaffData called - fetching staff data...');
  
  // Check if table element exists
  console.log('Staff table body element found:', !!staffTableBody);
  if (staffTableBody) {
    console.log('Staff table body HTML before fetch:', staffTableBody.innerHTML);
  }
  
  fetch('/roles/api/staff/')
    .then(response => {
      console.log('Staff response status:', response.status);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    })
    .then(data => {
      console.log('Staff data received:', data);
      // Render your staff table here
      if (staffTableBody) {
        if (data && data.length > 0) {
          const tableRows = data.map(staff => `
            <tr>
              <td>${staff.staff_name || ''}</td>
              <td>${staff.date_joined ? new Date(staff.date_joined).toLocaleDateString() : ''}</td>
              <td>${staff.email || ''}</td>
              <td>${staff.name || ''}</td>
              <td>${staff.location || ''}</td>
              <td>${staff.phm_id || ''}</td>
            </tr>
          `).join('');
          staffTableBody.innerHTML = tableRows;
          console.log('Staff table populated with', data.length, 'staff members');
          console.log('Staff table body HTML after population:', staffTableBody.innerHTML);
        } else {
          staffTableBody.innerHTML = '<tr><td colspan="6" class="text-center">No staff found</td></tr>';
          console.log('No staff found');
        }
      } else {
        console.error('Staff table body element not found');
      }
    })
    .catch((error) => {
      console.error("Error fetching staff data:", error);
      staffTableBody.innerHTML = `<tr><td colspan="5" class="text-center text-danger">Error loading staff. ${error}</td></tr>`;
    });
}

// ✅ On Page Load
document.addEventListener("DOMContentLoaded", () => {
  initPharmacyDropdowns();
  initPharmacyForm();
  initDeleteForms();
  initCreateManagerForm();
  initCreateStaffForm();
  initCreateAdminForm();
  initInventoryPage();
});