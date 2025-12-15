document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('tool1Form');
    const submitBtn = form.querySelector('button[type="submit"]');
    const loadingIndicator = document.getElementById('loadingIndicator');
    
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const fileInput = form.querySelector('input[type="file"]');
        const dateInput = form.querySelector('input[type="date"]');
        
        // Check if file is selected
        if (!fileInput.files.length) {
            alert("Please select a file");
            return;
        }
        
        // Show loading indicator
        loadingIndicator.style.display = 'flex';
        submitBtn.disabled = true;
        submitBtn.textContent = 'Generating...';
        
        try {
            // Create FormData
            const formData = new FormData();
            formData.append('excel_file', fileInput.files[0]);
            formData.append('as_of_date', dateInput.value);
            
            // Send request
            const response = await fetch(form.action, {
                method: 'POST',
                body: formData
            });
            
            if (response.ok) {
                // Get the blob
                const blob = await response.blob();
                
                // Create download link
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `Cost_Report_${dateInput.value}.pdf`;
                document.body.appendChild(a);
                a.click();
                
                // Cleanup
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                
                // Hide loading
                loadingIndicator.style.display = 'none';
                submitBtn.disabled = false;
                submitBtn.textContent = 'Generate PDF';
                
                // Reset form
                form.reset();
            } else {
                throw new Error('Failed to generate PDF');
            }
        } catch (error) {
            alert('Error generating PDF: ' + error.message);
            loadingIndicator.style.display = 'none';
            submitBtn.disabled = false;
            submitBtn.textContent = 'Generate PDF';
        }
    });
});