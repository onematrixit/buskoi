// app/static/js/script.js

// Function to navigate to a new page
function navigateTo(page) {
    window.location.href = page;
}

// Top toggle buttons
const homeToUniversityBtn = document.getElementById('homeToUniversity');
const universityToHomeBtn = document.getElementById('universityToHome');

// Location lists
const homeList = document.getElementById('home-list');
const universityList = document.getElementById('university-list');

// Toggle functionality for Home to University and University to Home
if (homeToUniversityBtn && universityToHomeBtn) {
    homeToUniversityBtn.addEventListener('click', () => {
        homeToUniversityBtn.classList.add('active');
        universityToHomeBtn.classList.remove('active');

        homeList.classList.remove('hidden');
        universityList.classList.add('hidden');
    });

    universityToHomeBtn.addEventListener('click', () => {
        universityToHomeBtn.classList.add('active');
        homeToUniversityBtn.classList.remove('active');

        universityList.classList.remove('hidden');
        homeList.classList.add('hidden');
    });
}

// Bottom navigation functionality
const navButtons = document.querySelectorAll('.nav-btn');

navButtons.forEach((button) => {
    button.addEventListener('click', () => {
        // Remove active state from all buttons
        navButtons.forEach((btn) => btn.classList.remove('active'));

        // Add active state to the clicked button
        button.classList.add('active');
    });
});

// Sidebar functionality
const sidebar = document.getElementById('sidebar');
const openSidebar = document.getElementById('openSidebar');
const closeSidebar = document.getElementById('closeSidebar');

// Open sidebar
if (openSidebar && sidebar) {
    openSidebar.addEventListener('click', () => {
        sidebar.classList.add('visible');
    });
}

// Close sidebar
if (closeSidebar && sidebar) {
    closeSidebar.addEventListener('click', () => {
        sidebar.classList.remove('visible');
    });
}

// Initialize Bootstrap tooltips
document.addEventListener('DOMContentLoaded', function () {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

// Dark Mode Toggle
const darkModeToggle = document.getElementById('darkModeToggle');

if (darkModeToggle) {
    const prefersDarkScheme = window.matchMedia("(prefers-color-scheme: dark)");

    // Check for saved user preference
    if (localStorage.getItem("darkMode") === "enabled") {
        document.body.classList.add("dark-mode");
        darkModeToggle.checked = true;
    } else if (localStorage.getItem("darkMode") === "disabled") {
        document.body.classList.remove("dark-mode");
        darkModeToggle.checked = false;
    } else if (prefersDarkScheme.matches) {
        document.body.classList.add("dark-mode");
        darkModeToggle.checked = true;
    }

    darkModeToggle.addEventListener('change', function () {
        if (this.checked) {
            document.body.classList.add("dark-mode");
            localStorage.setItem("darkMode", "enabled");
        } else {
            document.body.classList.remove("dark-mode");
            localStorage.setItem("darkMode", "disabled");
        }
    });
}
