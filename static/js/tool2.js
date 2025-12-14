const form2 = document.getElementById("tool2Form");
form2.addEventListener("submit", e => {
    const fileInput = form2.querySelector('input[type="file"]');
    if (!fileInput.files.length) {
        alert("Please select a file");
        e.preventDefault();
    }
});
