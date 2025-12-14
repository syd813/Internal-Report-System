const form = document.getElementById("tool1Form");
form.addEventListener("submit", e => {
    const fileInput = form.querySelector('input[type="file"]');
    if (!fileInput.files.length) {
        alert("Please select a file");
        e.preventDefault();
    }
});
