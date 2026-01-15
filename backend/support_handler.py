"""
Support System Handler
Manages student support tickets and admin support requests
"""
import pandas as pd
from pathlib import Path
from datetime import datetime
import json

class SupportHandler:
    def __init__(self, support_file='../data/support_tickets.xlsx'):
        self.support_file = Path(support_file)
        self.support_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize support tickets file if it doesn't exist
        if not self.support_file.exists():
            df = pd.DataFrame(columns=[
                'Ticket ID',
                'Student Name',
                'Registration No',
                'Email',
                'Subject',
                'Message',
                'Status',
                'Created At',
                'Resolved At',
                'Admin Notes'
            ])
            df.to_excel(self.support_file, index=False)
    
    def create_ticket(self, student_name, registration_no, email, subject, message):
        """Create a new support ticket from student"""
        try:
            # Load existing tickets
            df = pd.read_excel(self.support_file)
            
            # Generate ticket ID
            ticket_id = f"TKT{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Create new ticket
            new_ticket = pd.DataFrame([{
                'Ticket ID': ticket_id,
                'Student Name': student_name,
                'Registration No': registration_no,
                'Email': email,
                'Subject': subject,
                'Message': message,
                'Status': 'Open',
                'Created At': datetime.now(),
                'Resolved At': None,
                'Admin Notes': ''
            }])
            
            # Append to existing tickets
            df = pd.concat([df, new_ticket], ignore_index=True)
            df.to_excel(self.support_file, index=False)
            
            return True, ticket_id
        except Exception as e:
            print(f"Error creating ticket: {e}")
            return False, str(e)
    
    def get_all_tickets(self, status=None):
        """Get all support tickets, optionally filtered by status"""
        try:
            df = pd.read_excel(self.support_file)
            
            if status:
                df = df[df['Status'] == status]
            
            # Convert to list of dictionaries
            tickets = df.to_dict('records')
            
            # Format dates
            for ticket in tickets:
                if pd.notna(ticket.get('Created At')):
                    ticket['Created At'] = ticket['Created At'].strftime('%Y-%m-%d %H:%M:%S')
                if pd.notna(ticket.get('Resolved At')):
                    ticket['Resolved At'] = ticket['Resolved At'].strftime('%Y-%m-%d %H:%M:%S')
            
            return True, tickets
        except Exception as e:
            print(f"Error getting tickets: {e}")
            return False, []
    
    def get_ticket_by_id(self, ticket_id):
        """Get a specific ticket by ID"""
        try:
            df = pd.read_excel(self.support_file)
            ticket = df[df['Ticket ID'] == ticket_id]
            
            if ticket.empty:
                return False, "Ticket not found"
            
            ticket_dict = ticket.iloc[0].to_dict()
            
            # Format dates
            if pd.notna(ticket_dict.get('Created At')):
                ticket_dict['Created At'] = ticket_dict['Created At'].strftime('%Y-%m-%d %H:%M:%S')
            if pd.notna(ticket_dict.get('Resolved At')):
                ticket_dict['Resolved At'] = ticket_dict['Resolved At'].strftime('%Y-%m-%d %H:%M:%S')
            
            return True, ticket_dict
        except Exception as e:
            print(f"Error getting ticket: {e}")
            return False, str(e)
    
    def update_ticket_status(self, ticket_id, status, admin_notes=''):
        """Update ticket status and add admin notes"""
        try:
            df = pd.read_excel(self.support_file)
            
            # Find ticket
            ticket_index = df[df['Ticket ID'] == ticket_id].index
            
            if ticket_index.empty:
                return False, "Ticket not found"
            
            # Update status
            df.loc[ticket_index, 'Status'] = status
            
            if admin_notes:
                df.loc[ticket_index, 'Admin Notes'] = admin_notes
            
            # If resolving, set resolved date
            if status == 'Resolved':
                df.loc[ticket_index, 'Resolved At'] = datetime.now()
            
            df.to_excel(self.support_file, index=False)
            
            return True, "Ticket updated successfully"
        except Exception as e:
            print(f"Error updating ticket: {e}")
            return False, str(e)
    
    def get_ticket_stats(self):
        """Get statistics about support tickets"""
        try:
            df = pd.read_excel(self.support_file)
            
            stats = {
                'total_tickets': len(df),
                'open_tickets': len(df[df['Status'] == 'Open']),
                'in_progress_tickets': len(df[df['Status'] == 'In Progress']),
                'resolved_tickets': len(df[df['Status'] == 'Resolved'])
            }
            
            return True, stats
        except Exception as e:
            print(f"Error getting stats: {e}")
            return False, {}
