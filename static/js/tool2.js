document.addEventListener('DOMContentLoaded', function() {
    const form2 = document.getElementById('tool2Form');
    const submitBtn = form2.querySelector('button[type="submit"]');
    const loadingIndicator = document.getElementById('loadingIndicator');
    
    form2.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const fileInput = form2.querySelector('input[type="file"]');
        const dateFrom = form2.querySelector('input[name="date_from"]');
        const dateTill = form2.querySelector('input[name="date_till"]');
        const costCode = form2.querySelector('input[name="cost_code"]');
        
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
            if (dateFrom && dateFrom.value) formData.append('date_from', dateFrom.value);
            if (dateTill && dateTill.value) formData.append('date_till', dateTill.value);
            if (costCode && costCode.value) formData.append('cost_code', costCode.value);
            
            // Send request
            const response = await fetch(form2.action, {
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
                a.download = 'Detailed_Report.pdf';
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
                form2.reset();
            } else {
                const errorText = await response.text();
                throw new Error(errorText || 'Failed to generate PDF');
            }
        } catch (error) {
            alert('Error generating PDF: ' + error.message);
            loadingIndicator.style.display = 'none';
            submitBtn.disabled = false;
            submitBtn.textContent = 'Generate PDF';
        }
    });
});