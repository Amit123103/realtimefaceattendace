// Admin Management Functions

async function loadAdmins() {
    const tbody = document.getElementById('admins-table-body');
    tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; padding: 2rem; color: var(--text-muted);">Loading admins...</td></tr>';

    try {
        const response = await fetch(`${API_BASE_URL}/admin/manage/list-admins`, {
            headers: { 'Authorization': sessionToken }
        });

        const data = await response.json();

        if (data.success && data.data.length > 0) {
            tbody.innerHTML = data.data.map(admin => `
                <tr>
                    <td>${admin.Username}</td>
                    <td>${admin.Email || 'N/A'}</td>
                    <td>
                        <span class="role-badge role-${admin.Role}">
                            ${admin.Role.replace('_', ' ').toUpperCase()}
                        </span>
                    </td>
                    <td>
                        <span class="status-badge ${admin.Status === 'active' ? 'status-active' : 'status-inactive'}">
                            ${admin.Status}
                        </span>
                    </td>
                    <td>${admin['Created At'] || 'N/A'}</td>
                    <td>
                        <button class="btn-icon" onclick="editAdminRole('${admin.Username}')" title="Edit Role">
                            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M3 17.25V21H6.75L17.81 9.94L14.06 6.19L3 17.25ZM20.71 7.04C21.1 6.65 21.1 6.02 20.71 5.63L18.37 3.29C17.98 2.9 17.35 2.9 16.96 3.29L15.13 5.12L18.88 8.87L20.71 7.04Z" fill="currentColor"/>
                            </svg>
                        </button>
                        ${admin.Status === 'active' ? `
                            <button class="btn-icon btn-danger" onclick="deactivateAdmin('${admin.Username}')" title="Deactivate">
                                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                    <path d="M12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2ZM12 20C7.59 20 4 16.41 4 12C4 7.59 7.59 4 12 4C16.41 4 20 7.59 20 12C20 16.41 16.41 20 12 20ZM15.59 7L12 10.59L8.41 7L7 8.41L10.59 12L7 15.59L8.41 17L12 13.41L15.59 17L17 15.59L13.41 12L17 8.41L15.59 7Z" fill="currentColor"/>
                                </svg>
                            </button>
                        ` : ''}
                        <button class="btn-icon btn-danger" onclick="deleteAdmin('${admin.Username}')" title="Delete Permanently" style="color: #ef4444;">
                            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M6 19C6 20.1 6.9 21 8 21H16C17.1 21 18 20.1 18 19V7H6V19ZM19 4H15.5L14.5 3H9.5L8.5 4H5V6H19V4Z" fill="currentColor"/>
                            </svg>
                        </button>
                    </td>
                </tr>
            `).join('');
        } else {
            tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; padding: 2rem; color: var(--text-muted);">No admins found</td></tr>';
        }
    } catch (error) {
        console.error('Error loading admins:', error);
        tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; padding: 2rem; color: var(--error-color);">Error loading admins</td></tr>';
    }
}

function showAddAdminModal() {
    const username = prompt('Enter new admin username:');
    if (!username) return;

    const email = prompt('Enter admin email (optional):');
    const password = prompt('Enter password:');
    if (!password) return;

    const role = prompt('Enter role (super_admin, admin, or viewer):', 'admin');
    if (!role) return;

    addNewAdmin(username, password, role, email);
}

async function addNewAdmin(username, password, role, email = '') {
    try {
        const response = await fetch(`${API_BASE_URL}/admin/manage/add-admin`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': sessionToken
            },
            body: JSON.stringify({
                username: username,
                password: password,
                role: role,
                email: email
            })
        });

        const data = await response.json();

        if (data.success) {
            enhancedModal.showSuccess('Admin Added', `${username} has been added successfully!`);
            loadAdmins();
        } else {
            enhancedModal.showError('Error', data.message || 'Failed to add admin');
        }
    } catch (error) {
        console.error('Error adding admin:', error);
        enhancedModal.showError('Error', 'Network error while adding admin');
    }
}

async function editAdminRole(username) {
    const newRole = prompt(`Enter new role for ${username} (super_admin, admin, or viewer):`, 'admin');
    if (!newRole) return;

    try {
        const response = await fetch(`${API_BASE_URL}/admin/manage/update-role`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': sessionToken
            },
            body: JSON.stringify({
                username: username,
                role: newRole
            })
        });

        const data = await response.json();

        if (data.success) {
            enhancedModal.showSuccess('Role Updated', `${username}'s role has been updated to ${newRole}`);
            loadAdmins();
        } else {
            enhancedModal.showError('Error', data.message || 'Failed to update role');
        }
    } catch (error) {
        console.error('Error updating role:', error);
        enhancedModal.showError('Error', 'Network error while updating role');
    }
}

async function deactivateAdmin(username) {
    if (!confirm(`Are you sure you want to deactivate ${username}?`)) return;

    try {
        const response = await fetch(`${API_BASE_URL}/admin/manage/deactivate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': sessionToken
            },
            body: JSON.stringify({
                username: username
            })
        });

        const data = await response.json();

        if (data.success) {
            enhancedModal.showSuccess('Admin Deactivated', `${username} has been deactivated`);
            loadAdmins();
        } else {
            enhancedModal.showError('Error', data.message || 'Failed to deactivate admin');
        }
    } catch (error) {
        console.error('Error deactivating admin:', error);
        enhancedModal.showError('Error', 'Network error while deactivating admin');
    }
}

async function deleteAdmin(username) {
    if (!confirm(`Are you sure you want to PERMANENTLY DELETE admin "${username}"?\nThis action cannot be undone.`)) return;

    try {
        const response = await fetch(`${API_BASE_URL}/admin/manage/delete`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': sessionToken
            },
            body: JSON.stringify({
                username: username
            })
        });

        const data = await response.json();

        if (data.success) {
            enhancedModal.showSuccess('Admin Deleted', `${username} has been permanently deleted.`);
            loadAdmins();
        } else {
            enhancedModal.showError('Error', data.message || 'Failed to delete admin');
        }
    } catch (error) {
        console.error('Error deleting admin:', error);
        enhancedModal.showError('Error', 'Network error while deleting admin');
    }
}

// Add to existing showSection function
// Add this case in the showSection function after analytics:
// } else if (sectionId === 'admin-management') {
//     loadAdmins();
// }
