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
  fetch(url)
    .then((response) => {
      if (!response.ok) throw new Error("Page not found");
      return response.text();
    })
    .then((html) => {
      document.getElementById("content-area").innerHTML = html;
      initPharmacyDropdowns();
      initPharmacyForm();
      initDeleteForms();
      initCreateManagerForm();
      initCreateStaffForm();
      initCreateAdminForm();
    })
    .catch(() => {
      document.getElementById("content-area").innerHTML =
        "<h3>Page not found.</h3>";
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
        .then((data) => {
          dropdownMenu.innerHTML = "";

          if (!data.length) {
            dropdownMenu.innerHTML = "<li>No pharmacies found</li>";
            return;
          }

          data.forEach((pharmacy) => {
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

// ✅ Load Pharmacies in Sidebar
// function loadPharmacies() {
//   const submenu = document.getElementById("pharmacies-submenu");
//   submenu.innerHTML =
//     "<li class='nav-item'><span class='nav-link'>Loading...</span></li>";

//   fetch("/pharmacy/api/pharmacies/")
//     .then((response) => response.json())
//     .then((data) => {
//       if (Array.isArray(data) && data.length > 0) {
//         submenu.innerHTML = "";
//         data.forEach((pharmacy) => {
//           const li = document.createElement("li");
//           li.className = "nav-item";

//           li.innerHTML = `
//             <a class="nav-link d-flex align-items-center" onclick="togglePharmacySubmenu(${pharmacy.id}, this); setActiveNavLink(this);">
//               <i class="bi bi-shop"></i>
//               <span class="nav-text">${pharmacy.name}</span>
//               <i class="bi bi-caret-right-fill ms-auto text-black nav-text"></i>
//             </a>
//             <ul id="submenu-${pharmacy.id}" class="nav flex-column ms-3 d-none"></ul>
//           `;

//           submenu.appendChild(li);
//         });
//       } else {
//         submenu.innerHTML =
//           "<li class='nav-item'><span class='nav-link'>No pharmacies found</span></li>";
//       }
//     })
//     .catch(() => {
//       submenu.innerHTML =
//         "<li class='nav-item'><span class='nav-link text-danger'>Error loading data</span></li>";
//     });
// }

// ✅ Toggle Pharmacy Submenu with Rotation and Content
// function togglePharmacySubmenu(pharmacyId, clickedElement) {
//   const submenu = document.getElementById(`submenu-${pharmacyId}`);

//   // Close other submenus
//   document.querySelectorAll("ul[id^='submenu-']").forEach((el) => {
//     if (el.id !== `submenu-${pharmacyId}`) {
//       el.classList.add("d-none");
//       const prev = el.previousElementSibling;
//       if (prev) {
//         const otherIcon = prev.querySelector("i.bi-caret-right-fill");
//         if (otherIcon) otherIcon.classList.remove("rotate-down");
//       }
//     }
//   });

//   // Toggle current submenu
//   submenu.classList.toggle("d-none");

//   // Load submenu items once
//   if (submenu.children.length === 0) {
//     submenu.innerHTML = `
//       <li class="nav-item"><a class="nav-link" onclick="loadPage('pharmacy/${pharmacyId}/inventory')">Inventory</a></li>
//       <li class="nav-item"><a class="nav-link" onclick="loadPage('pharmacy/${pharmacyId}/sales')">Sales</a></li>
//       <li class="nav-item"><a class="nav-link" onclick="loadPage('pharmacy/${pharmacyId}/manager')">See Manager</a></li>
//     `;
//   }

//   // Handle icon rotation
//   const icon = clickedElement.querySelector("i.bi-caret-right-fill");
//   if (icon) {
//     icon.classList.toggle("rotate-down", !submenu.classList.contains("d-none"));
//   }
// }

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
            const row = document.getElementById(`pharmacy-row-${pharmacyId}`);
            if (row) row.remove();
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
// select pharmacies in delete-pharmacy table.%
let selectedPharmacyIds = new Set();
function selectPharmacy(id, forceSelect = null) {
  const row = document.getElementById("pharmacy-row-" + id);
  const checkbox = row.querySelector(".pharmacy-checkbox");
  const shouldSelect =
    forceSelect !== null ? forceSelect : !selectedPharmacyIds.has(id);

  if (shouldSelect) {
    selectedPharmacyIds.add(id);
    checkbox.checked = true;
    // row.style.backgroundColor = "#d1e7dd"; // selected color
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
  // Prevent double toggle when clicking on checkbox
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

// ✅ Allow checkbox clicks to toggle selection
document.addEventListener("DOMContentLoaded", function () {
  initDeleteForms();

  document.querySelectorAll(".pharmacy-checkbox").forEach((checkbox) => {
    checkbox.addEventListener("click", function (e) {
      e.stopPropagation(); // Prevent row click triggering twice
      const id = parseInt(this.value);
      selectPharmacy(id);
    });
  });
});

// ✅ Create-Manager-Form-Submission
function initCreateManagerForm() {
  const submitBtn = document.getElementById("submitBtn");
  const form = document.getElementById("createManagerForm");
  if (!submitBtn || !form) return;

  submitBtn.addEventListener("click", function (e) {
    e.preventDefault();

    // ✅ Sahi selector
    const selectedPharmacies = document.querySelectorAll(
      'input[name="pharmacies"]:checked'
    );

    // ✅ Alert only if none selected
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

    // ✅ Check if a radio is selected
    const selectedPharmacy = form.querySelector(
      'input[name="pharmacies"]:checked'
    );

    if (!selectedPharmacy) {
      // ❌ No selection made — show alert
      alert("At-Least 1 Pharmacy must be Added");
      return;
    }

    // ✅ Proceed with submission
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
      pharmacies: [selectedPharmacy.value], // send selected radio pharmacy
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
        } else {
          alert("Error: " + (data.error || "Could not create staff."));
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

// ✅ On Page Load
document.addEventListener("DOMContentLoaded", () => {
  initPharmacyDropdowns();
  initPharmacyForm();
  initDeleteForms();
  initCreateManagerForm();
  initCreateStaffForm();
  initCreateAdminForm();
});
