# Study Hours Tracking Application

A web-based application for tracking student study hours. This app was built using **Flask** for the backend and **HTML/CSS** for the frontend, with role-based access for students and admins. It allows users to upload CSV files to track study hours and view their accumulated data on a personalised dashboard.

## Features

- **User Authentication**: Unique usernames for students and admins with role-based access.
- **CSV File Upload**: Students can upload study hours in CSV format, with data stored separately per user.
- **Role-Based Dashboards**:
  - **Students**: Access a personal dashboard to track accumulated study hours, filter by month, and view total hours.
  - **Admins**: View and filter study data for all students by name and month.
- **Dynamic Filtering**: Users and admins can filter study hours by month, with reports updating dynamically.
- **Improved UI**: CSS styling for a user-friendly and responsive interface.

## Getting Started

### Prerequisites

- **Python 3.x**: Ensure Python is installed on your machine.
- **Flask**: Install Flask via pip if it's not already installed.

pip install Flask

Installation

	1.	Clone the repository:
git clone https://github.com/your-username/study-hours-tracking.git
cd study-hours-tracking


	2.	Set up the environment:
It’s recommended to create a virtual environment to manage dependencies.

python -m venv venv
source venv/bin/activate    # On Windows, use `venv\Scripts\activate`


	3.	Install dependencies:

pip install -r requirements.txt


	4.	Run the Application:
Start the Flask app by running:

python app.py


	5.	Access the App:
Open a web browser and navigate to http://127.0.0.1:5000 to start using the application.

Usage

	1.	Login:
	•	Students: Enter your unique username and password to access your personal dashboard.
	•	Admins: Log in with admin credentials to access the admin dashboard. (username and pw: ADMIN)
	2.	Upload Study Hours:
	•	Students can upload a CSV file with study hours. The app parses the CSV and updates the dashboard with new hours.
	3.	Filter Data:
	•	Use the filtering options on the dashboard to view data for specific months. Admins can filter by student name and month.
	4.	Logout:
	•	After uploading or reviewing hours, you can log out to end your session securely.

File Structure
![File Structure](https://github.com/Kautharr/student_report_app/blob/main/file_structure.png)


