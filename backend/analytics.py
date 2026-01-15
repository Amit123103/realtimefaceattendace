from collections import defaultdict
from datetime import datetime, timedelta
import pandas as pd

class AnalyticsEngine:
    def __init__(self, excel_handler):
        self.excel_handler = excel_handler
    
    def get_daily_attendance(self, days=7):
        """Get daily attendance counts for the last N days"""
        try:
            attendance = self.excel_handler.get_attendance_records()
            
            # Group by date
            daily_counts = defaultdict(int)
            for record in attendance:
                date = record.get('Date')
                if date:
                    daily_counts[date] += 1
            
            # Sort by date and get last N days
            sorted_dates = sorted(daily_counts.keys(), reverse=True)[:days]
            
            result = {
                'labels': sorted_dates[::-1],  # Reverse to show oldest first
                'data': [daily_counts[date] for date in sorted_dates[::-1]]
            }
            
            return True, result
        except Exception as e:
            print(f"Error getting daily attendance: {e}")
            return False, {}
    
    def get_weekly_trends(self, weeks=4):
        """Get weekly attendance trends"""
        try:
            attendance = self.excel_handler.get_attendance_records()
            
            # Group by week
            weekly_counts = defaultdict(int)
            for record in attendance:
                date_str = record.get('Date')
                if date_str:
                    try:
                        date = pd.to_datetime(date_str)
                        week = date.strftime('%Y-W%U')  # Year-Week format
                        weekly_counts[week] += 1
                    except:
                        continue
            
            # Get last N weeks
            sorted_weeks = sorted(weekly_counts.keys(), reverse=True)[:weeks]
            
            result = {
                'labels': sorted_weeks[::-1],
                'data': [weekly_counts[week] for week in sorted_weeks[::-1]]
            }
            
            return True, result
        except Exception as e:
            print(f"Error getting weekly trends: {e}")
            return False, {}
    
    def get_student_attendance_percentage(self):
        """Get attendance percentage for each student"""
        try:
            students = self.excel_handler.get_all_students()
            attendance = self.excel_handler.get_attendance_records()
            
            # Count total working days (unique dates in attendance)
            unique_dates = set(record.get('Date') for record in attendance if record.get('Date'))
            total_days = len(unique_dates) if unique_dates else 1
            
            # Calculate percentage for each student
            student_percentages = []
            for student in students:
                reg_no = student.get('Registration No')
                name = student.get('Name')
                
                # Count attendance for this student
                student_attendance = [r for r in attendance if r.get('Registration No') == reg_no]
                count = len(student_attendance)
                percentage = (count / total_days * 100) if total_days > 0 else 0
                
                student_percentages.append({
                    'name': name,
                    'registration_no': reg_no,
                    'attendance_count': count,
                    'total_days': total_days,
                    'percentage': round(percentage, 2)
                })
            
            return True, student_percentages
        except Exception as e:
            print(f"Error calculating student percentages: {e}")
            return False, []
    
    def get_monthly_overview(self):
        """Get monthly attendance overview"""
        try:
            attendance = self.excel_handler.get_attendance_records()
            
            # Group by month
            monthly_counts = defaultdict(int)
            for record in attendance:
                date_str = record.get('Date')
                if date_str:
                    try:
                        date = pd.to_datetime(date_str)
                        month = date.strftime('%Y-%m')  # Year-Month format
                        monthly_counts[month] += 1
                    except:
                        continue
            
            # Get last 6 months
            sorted_months = sorted(monthly_counts.keys(), reverse=True)[:6]
            
            result = {
                'labels': sorted_months[::-1],
                'data': [monthly_counts[month] for month in sorted_months[::-1]]
            }
            
            return True, result
        except Exception as e:
            print(f"Error getting monthly overview: {e}")
            return False, {}
    
    def get_summary_stats(self):
        """Get overall summary statistics"""
        try:
            students = self.excel_handler.get_all_students()
            attendance = self.excel_handler.get_attendance_records()
            
            # Get today's attendance
            today = datetime.now().strftime('%Y-%m-%d')
            today_attendance = [r for r in attendance if r.get('Date') == today]
            
            # Get unique dates
            unique_dates = set(record.get('Date') for record in attendance if record.get('Date'))
            
            # Calculate average daily attendance
            avg_daily = len(attendance) / len(unique_dates) if unique_dates else 0
            
            stats = {
                'total_students': len(students),
                'total_attendance_records': len(attendance),
                'today_attendance': len(today_attendance),
                'total_working_days': len(unique_dates),
                'average_daily_attendance': round(avg_daily, 2)
            }
            
            return True, stats
        except Exception as e:
            print(f"Error getting summary stats: {e}")
            return False, {}
