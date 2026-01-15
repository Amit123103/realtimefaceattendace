// Support System JavaScript for Admin Panel - Add to admin.js

// Load Support Tickets
async function loadSupportTickets() {
    const tbody = document.getElementById('support-tickets-tbody');
    tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; padding: 2rem;">Loading tickets...</td></tr>';

    try {
        const response = await fetch(`${API_BASE_URL}/admin/support/tickets`, {
            headers: { 'Authorization': sessionToken }
        });

        const data = await response.json();

        if (data.success && data.data.length > 0) {
            tbody.innerHTML = data.data.map(ticket => `
                <tr>
                    <td>${ticket['Ticket ID']}</td>
                    <td>${ticket['Student Name']}<br><small style="color: var(--text-secondary);">${ticket['Registration No']}</small></td>
                    <td>${ticket.Subject}</td>
                    <td><span class="status-badge status-${ticket.Status.toLowerCase().replace(' ', '-')}">${ticket.Status}</span></td>
                    <td>${ticket['Created At']}</td>
                    <td>
                        <button class="btn-icon" onclick="viewTicket('${ticket['Ticket ID']}')" title="View Details">
                            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M12 4.5C7 4.5 2.73 7.61 1 12C2.73 16.39 7 19.5 12 19.5C17 19.5 21.27 16.39 23 12C21.27 7.61 17 4.5 12 4.5ZM12 17C9.24 17 7 14.76 7 12C7 9.24 9.24 7 12 7C14.76 7 17 9.24 17 12C17 14.76 14.76 17 12 17ZM12 9C10.34 9 9 10.34 9 12C9 13.66 10.34 15 12 15C13.66 15 15 13.66 15 12C15 10.34 13.66 9 12 9Z" fill="currentColor"/>
                            </svg>
                        </button>
                        ${ticket.Status !== 'Resolved' ? `
                            <button class="btn-icon" onclick="updateTicketStatus('${ticket['Ticket ID']}', 'Resolved')" title="Mark Resolved">
                                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                    <path d="M9 16.17L4.83 12L3.41 13.41L9 19L21 7L19.59 5.59L9 16.17Z" fill="currentColor"/>
                                </svg>
                            </button>
                        ` : ''}
                    </td>
                </tr>
            `).join('');
        } else {
            tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; padding: 2rem;">No support tickets found</td></tr>';
        }

        // Load stats
        loadSupportStats();
    } catch (error) {
        console.error('Error loading tickets:', error);
        tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; padding: 2rem; color: var(--error-color);">Error loading tickets</td></tr>';
    }
}

async function loadSupportStats() {
    try {
        const response = await fetch(`${API_BASE_URL}/admin/support/stats`, {
            headers: { 'Authorization': sessionToken }
        });

        const data = await response.json();

        if (data.success) {
            const stats = data.data;
            document.getElementById('total-tickets-stat').textContent = stats.total_tickets || 0;
            document.getElementById('open-tickets-stat').textContent = stats.open_tickets || 0;
            document.getElementById('progress-tickets-stat').textContent = stats.in_progress_tickets || 0;
            document.getElementById('resolved-tickets-stat').textContent = stats.resolved_tickets || 0;
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

async function viewTicket(ticketId) {
    try {
        const response = await fetch(`${API_BASE_URL}/admin/support/ticket/${ticketId}`, {
            headers: { 'Authorization': sessionToken }
        });

        const data = await response.json();

        if (data.success) {
            const ticket = data.data;
            const message = `
                Student: ${ticket['Student Name']} (${ticket['Registration No']})
                Email: ${ticket.Email || 'N/A'}
                Subject: ${ticket.Subject}
                Status: ${ticket.Status}
                Created: ${ticket['Created At']}
                
                Message:
                ${ticket.Message}
                
                Admin Notes: ${ticket['Admin Notes'] || 'None'}
            `;
            alert(message);
        }
    } catch (error) {
        console.error('Error viewing ticket:', error);
        enhancedModal.showError('Error', 'Could not load ticket details');
    }
}

async function updateTicketStatus(ticketId, status) {
    const notes = prompt('Add admin notes (optional):');

    try {
        const response = await fetch(`${API_BASE_URL}/admin/support/update-ticket`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': sessionToken
            },
            body: JSON.stringify({
                ticket_id: ticketId,
                status: status,
                admin_notes: notes || ''
            })
        });

        const data = await response.json();

        if (data.success) {
            enhancedModal.showSuccess('Ticket Updated', `Ticket ${ticketId} marked as ${status}`);
            loadSupportTickets();
        } else {
            enhancedModal.showError('Error', data.message);
        }
    } catch (error) {
        console.error('Error updating ticket:', error);
        enhancedModal.showError('Error', 'Could not update ticket');
    }
}

// Admin Support Request
document.getElementById('admin-support-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();

    const subject = document.getElementById('admin-support-subject').value;
    const message = document.getElementById('admin-support-message').value;

    try {
        const response = await fetch(`${API_BASE_URL}/admin/support/request-help`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': sessionToken
            },
            body: JSON.stringify({
                subject: subject,
                message: message
            })
        });

        const data = await response.json();

        if (data.success) {
            enhancedModal.showSuccess(
                'Support Request Sent!',
                'Your request has been sent to the system administrator at amitsingh6394366374@gmail.com'
            );
            document.getElementById('admin-support-form').reset();
        } else {
            enhancedModal.showError('Error', data.message);
        }
    } catch (error) {
        console.error('Error sending support request:', error);
        enhancedModal.showError('Error', 'Could not send support request');
    }
});

// Update showSection to load support tickets
// Add this case in showSection function:
// } else if (sectionId === 'student-support') {
//     loadSupportTickets();
// }
