document.addEventListener('DOMContentLoaded', function() {
    // Admin stack management
    const createStackBtn = document.getElementById('create-stack-btn');
    const stackFormModal = document.getElementById('stack-form-modal');
    const closeModal = document.querySelector('.close');
    const stackForm = document.getElementById('stack-form');
    
    if (createStackBtn) {
        createStackBtn.addEventListener('click', function() {
            document.getElementById('form-title').textContent = 'Create New Stack';
            stackForm.reset();
            document.getElementById('stack-id').value = '';
            stackFormModal.style.display = 'block';
        });
    }
    
    if (closeModal) {
        closeModal.addEventListener('click', function() {
            stackFormModal.style.display = 'none';
        });
    }
    
    window.addEventListener('click', function(event) {
        if (event.target === stackFormModal) {
            stackFormModal.style.display = 'none';
        }
    });
    
    if (stackForm) {
        stackForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(stackForm);
            const stackData = {
                name: formData.get('name'),
                description: formData.get('description'),
                bet_price: parseInt(formData.get('bet_price')),
                winning_probability: parseFloat(formData.get('winning_probability')),
                fee_percentage: parseFloat(formData.get('fee_percentage')),
                enabled: formData.get('enabled') === 'on'
            };
            
            const stackId = document.getElementById('stack-id').value;
            
            // In a real implementation, this would make an API call to create/update the stack
            console.log('Stack data:', stackData);
            console.log('Stack ID (for update):', stackId);
            
            // Close the modal
            stackFormModal.style.display = 'none';
            
            // Show success message
            alert('Stack ' + (stackId ? 'updated' : 'created') + ' successfully!');
            
            // Reload the page to show updated data
            location.reload();
        });
    }
    
    // Edit stack buttons
    const editButtons = document.querySelectorAll('.edit-stack');
    editButtons.forEach(button => {
        button.addEventListener('click', function() {
            const stackId = this.getAttribute('data-stack-id');
            // In a real implementation, this would fetch the stack data and populate the form
            console.log('Editing stack:', stackId);
            
            // For demo purposes, just show the modal
            document.getElementById('form-title').textContent = 'Edit Stack';
            document.getElementById('stack-id').value = stackId;
            stackFormModal.style.display = 'block';
        });
    });
    
    // Delete stack buttons
    const deleteButtons = document.querySelectorAll('.delete-stack');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function() {
            const stackId = this.getAttribute('data-stack-id');
            if (confirm('Are you sure you want to delete this stack?')) {
                // In a real implementation, this would make an API call to delete the stack
                console.log('Deleting stack:', stackId);
                alert('Stack deleted successfully!');
                // Reload the page to show updated data
                location.reload();
            }
        });
    });
});