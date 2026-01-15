// Analytics Dashboard JavaScript for Admin Panel

const AnalyticsDashboard = {
    charts: {},

    async init() {
        await this.loadAnalytics();
        this.setupRefreshButton();
    },

    async loadAnalytics() {
        const sessionToken = localStorage.getItem('admin_session');
        if (!sessionToken) return;

        try {
            // Load summary stats
            await this.loadSummaryStats(sessionToken);

            // Load charts
            await this.loadDailyChart(sessionToken);
            await this.loadWeeklyChart(sessionToken);
            await this.loadStudentPercentages(sessionToken);
        } catch (error) {
            console.error('Error loading analytics:', error);
            showNotification('Error loading analytics data', 'error');
        }
    },

    async loadSummaryStats(sessionToken) {
        const response = await fetch(`${API_BASE_URL}/admin/analytics/summary`, {
            headers: { 'Authorization': sessionToken }
        });

        const data = await response.json();

        if (data.success) {
            const stats = data.data;
            document.getElementById('total-students-stat').textContent = stats.total_students || 0;
            document.getElementById('total-attendance-stat').textContent = stats.total_attendance_records || 0;
            document.getElementById('today-attendance-stat').textContent = stats.today_attendance || 0;
            document.getElementById('avg-daily-stat').textContent = stats.average_daily_attendance?.toFixed(1) || 0;
        }
    },

    async loadDailyChart(sessionToken) {
        const response = await fetch(`${API_BASE_URL}/admin/analytics/daily?days=7`, {
            headers: { 'Authorization': sessionToken }
        });

        const data = await response.json();

        if (data.success) {
            const ctx = document.getElementById('dailyChart');
            if (!ctx) return;

            if (this.charts.daily) {
                this.charts.daily.destroy();
            }

            this.charts.daily = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: data.data.labels,
                    datasets: [{
                        label: 'Daily Attendance',
                        data: data.data.data,
                        backgroundColor: 'rgba(99, 102, 241, 0.5)',
                        borderColor: 'rgb(99, 102, 241)',
                        borderWidth: 2,
                        borderRadius: 8
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        },
                        title: {
                            display: true,
                            text: 'Last 7 Days Attendance',
                            color: '#e2e8f0',
                            font: {
                                size: 16,
                                weight: 'bold'
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                color: '#94a3b8',
                                stepSize: 1
                            },
                            grid: {
                                color: 'rgba(148, 163, 184, 0.1)'
                            }
                        },
                        x: {
                            ticks: {
                                color: '#94a3b8'
                            },
                            grid: {
                                display: false
                            }
                        }
                    }
                }
            });
        }
    },

    async loadWeeklyChart(sessionToken) {
        const response = await fetch(`${API_BASE_URL}/admin/analytics/weekly?weeks=4`, {
            headers: { 'Authorization': sessionToken }
        });

        const data = await response.json();

        if (data.success) {
            const ctx = document.getElementById('weeklyChart');
            if (!ctx) return;

            if (this.charts.weekly) {
                this.charts.weekly.destroy();
            }

            this.charts.weekly = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.data.labels,
                    datasets: [{
                        label: 'Weekly Attendance',
                        data: data.data.data,
                        borderColor: 'rgb(16, 185, 129)',
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        },
                        title: {
                            display: true,
                            text: 'Weekly Trends',
                            color: '#e2e8f0',
                            font: {
                                size: 16,
                                weight: 'bold'
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                color: '#94a3b8'
                            },
                            grid: {
                                color: 'rgba(148, 163, 184, 0.1)'
                            }
                        },
                        x: {
                            ticks: {
                                color: '#94a3b8'
                            },
                            grid: {
                                display: false
                            }
                        }
                    }
                }
            });
        }
    },

    async loadStudentPercentages(sessionToken) {
        const response = await fetch(`${API_BASE_URL}/admin/analytics/student-percentages`, {
            headers: { 'Authorization': sessionToken }
        });

        const data = await response.json();

        if (data.success) {
            const ctx = document.getElementById('percentageChart');
            if (!ctx) return;

            if (this.charts.percentage) {
                this.charts.percentage.destroy();
            }

            // Get top 10 students
            const topStudents = data.data.slice(0, 10);

            this.charts.percentage = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: topStudents.map(s => s.name),
                    datasets: [{
                        data: topStudents.map(s => s.percentage),
                        backgroundColor: [
                            'rgba(99, 102, 241, 0.8)',
                            'rgba(16, 185, 129, 0.8)',
                            'rgba(245, 158, 11, 0.8)',
                            'rgba(239, 68, 68, 0.8)',
                            'rgba(139, 92, 246, 0.8)',
                            'rgba(236, 72, 153, 0.8)',
                            'rgba(14, 165, 233, 0.8)',
                            'rgba(34, 197, 94, 0.8)',
                            'rgba(251, 146, 60, 0.8)',
                            'rgba(168, 85, 247, 0.8)'
                        ],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'right',
                            labels: {
                                color: '#e2e8f0',
                                padding: 15,
                                font: {
                                    size: 12
                                }
                            }
                        },
                        title: {
                            display: true,
                            text: 'Top 10 Students Attendance %',
                            color: '#e2e8f0',
                            font: {
                                size: 16,
                                weight: 'bold'
                            }
                        }
                    }
                }
            });
        }
    },

    setupRefreshButton() {
        const refreshBtn = document.getElementById('refresh-analytics-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.loadAnalytics();
                showNotification('Analytics refreshed', 'success');
            });
        }
    },

    async downloadPDFReport() {
        const sessionToken = localStorage.getItem('admin_session');
        if (!sessionToken) return;

        try {
            const response = await fetch(`${API_BASE_URL}/admin/generate-pdf-report`, {
                headers: { 'Authorization': sessionToken }
            });

            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `attendance_report_${new Date().toISOString().split('T')[0]}.pdf`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);

                enhancedModal.showSuccess('PDF Downloaded', 'Attendance report has been downloaded successfully');
            } else {
                enhancedModal.showError('Download Failed', 'Could not generate PDF report');
            }
        } catch (error) {
            console.error('Error downloading PDF:', error);
            enhancedModal.showError('Error', 'Failed to download PDF report');
        }
    },

    async sendEmailReport() {
        const email = prompt('Enter email address to send report:');
        if (!email) return;

        const sessionToken = localStorage.getItem('admin_session');
        if (!sessionToken) return;

        try {
            const response = await fetch(`${API_BASE_URL}/admin/send-email-report`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': sessionToken
                },
                body: JSON.stringify({ email: email })
            });

            const data = await response.json();

            if (data.success) {
                enhancedModal.showSuccess('Email Sent', `Report has been sent to ${email}`);
            } else {
                enhancedModal.showError('Email Failed', data.message || 'Could not send email');
            }
        } catch (error) {
            console.error('Error sending email:', error);
            enhancedModal.showError('Error', 'Failed to send email report');
        }
    }
};

// Export for use in admin.js
window.AnalyticsDashboard = AnalyticsDashboard;
