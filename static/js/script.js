document.addEventListener('DOMContentLoaded', function() {
    const tableBody = document.querySelector('#panelTable tbody');

    tableBody.addEventListener('click', function(event) {
        if (event.target.classList.contains('addRow')) {
            const newRow = document.createElement('tr');
            newRow.innerHTML = `
                <td><input type="number" name="length[]" class="form-control" min="0" step="any" required></td>
                <td><input type="number" name="width[]" class="form-control" min="0" step="any" required></td>
                <td><input type="number" name="quantity[]" class="form-control" min="0" step="any" required></td>
                <td><button type="button" class="btn btn-danger removeRow">-</button></td>
            `;
            tableBody.appendChild(newRow);
        } else if (event.target.classList.contains('removeRow')) {
            const row = event.target.parentNode.parentNode;
            row.parentNode.removeChild(row);
        }
    });

    // Import CSV file validation
    document.getElementById('csv_file_input').addEventListener('change', function() {
        let fileInput = this;
        let submitButton = document.getElementById('csv_file_submit_btn');

        // Check if any file is selected and if it is a CSV file
        if (fileInput.files.length > 0) {
            let fileType = fileInput.files[0].type;
            if(fileType === "text/csv" || fileType === "application/vnd.ms-excel"){
                submitButton.disabled = false;
                Swal.fire({
                    title: 'Success!',
                    text: 'File Uploaded Successfully.',
                    icon: 'success'
                })
            }
            else{
                Swal.fire({
                    title: 'Error!',
                    text: 'Only CSV Files Supported.',
                    icon: 'error'
                })
                submitButton.disabled = true;
            }
        } else {
            Swal.fire({
                title: 'Error!',
                text: 'Please Upload a file first.',
                icon: 'error'
            })
            submitButton.disabled = true;
        }
    });
});

