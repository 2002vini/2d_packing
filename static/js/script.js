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
});