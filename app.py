

from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import csv
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'secret_key_123'  

# Directory where uploaded files will be stored
UPLOAD_FOLDER = 'uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# In-memory database
users_db = {
    'ADMIN': {'password': generate_password_hash('ADMIN'), 'hours': {}, 'registered_name': 'ADMIN'}
}  # Store user data
student_data = {}  # Cumulative study hours for each student by month

# Ensure uploads folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def read_study_hours(file_path):
    """Read and sum study hours from a CSV file."""
    study_data = {}
    with open(file_path, newline='') as file:
        reader = csv.reader(file)
        next(reader)  
        for row in reader:
            if len(row) < 2:
                continue  # ommit rows that don't have at least 2 columns (subject, hours)
            try:
                subject, hours = row[0], int(row[1])
                if subject in study_data:
                    study_data[subject] += hours
                else:
                    study_data[subject] = hours
            except ValueError:
                continue  # omit rows with invalid data
    return study_data

def generate_report(student_name, study_data, month_str):
    """Generate a report of study hours for a student."""
    total_hours = sum(study_data.values())
    report = f'Study Hours Report for "{student_name}" for the month of "{month_str}":\n'
    for idx, (subject, hours) in enumerate(study_data.items(), start=1):
        hour_label = "hour" if hours == 1 else "hours"
        report += f'{idx}. {subject}: {hours} {hour_label}.\n'
    report += f'{len(study_data) + 1}. Total Study Hours: {total_hours} hours.\n'
    return report

def format_month_year(month_input):
    """Convert 'YYYY-MM' to 'Month YYYY' (e.g., 'October 2024')."""
    return datetime.strptime(month_input, '%Y-%m').strftime('%B %Y')

@app.route("/")
def home():
    """Home page with options to register or login."""
    if 'username' in session:
        # If user is already logged in, redirect them to the upload page
        return redirect(url_for('upload_file'))
    return render_template('home.html')  # Shows options for login or register

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register a new student."""
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        registered_name = request.form['registered_name'].upper()  # Ensure all uppercase for Student-Registered Name
        
        if username in users_db:
            return "User already exists!", 400

        # Store the user with a hashed password and registered name
        users_db[username] = {'password': generate_password_hash(password), 'hours': {}, 'registered_name': registered_name}
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route("/login", methods=["GET", "POST"])
def login():
    """Login a student or admin."""
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        user = users_db.get(username)
        if not user or not check_password_hash(user['password'], password):
            return "Invalid username or password!", 400

        # Set session with username
        session['username'] = username

        # Redirect admin to admin page, others to upload page
        if username == 'ADMIN':
            return redirect(url_for('admin'))
        return redirect(url_for('upload_file'))

    return render_template('login.html')

@app.route("/logout")
def logout():
    """Logout the current user."""
    session.pop('username', None)
    return redirect(url_for('home'))

@app.route("/upload", methods=["GET", "POST"])
def upload_file():
    """Upload a CSV file with study hours for a logged-in student."""
    # Ensure user is logged in
    if 'username' not in session:
        return redirect(url_for('login'))

    student_name = session['username']

    if request.method == "POST":
        # Check if a file is uploaded
        if 'file' not in request.files:
            return "No file uploaded", 400

        file = request.files['file']

        if file.filename == '':
            return "No file selected", 400

        # Get the month and year from the form
        month = request.form['month']

        # Format the month in "Month YYYY" format (e.g., "October 2024")
        formatted_month = format_month_year(month)

        # Save the file to the uploads folder
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        # Read the study data from the uploaded file
        study_data = read_study_hours(file_path)

        # Update the student's cumulative study hours for the selected month
        if student_name not in student_data:
            student_data[student_name] = {}

        if formatted_month in student_data[student_name]:
            for subject, hours in study_data.items():
                if subject in student_data[student_name][formatted_month]:
                    student_data[student_name][formatted_month][subject] += hours
                else:
                    student_data[student_name][formatted_month][subject] = hours
        else:
            student_data[student_name][formatted_month] = study_data

        # Redirect to the logout page after successful upload
        return redirect(url_for('upload_success'))

    return render_template('upload.html')

@app.route("/upload-success")
def upload_success():
    """Logout confirmation page after file upload."""
    return render_template('upload_success.html')

@app.route("/admin", methods=["GET", "POST"])
def admin():
    """Admin page to view all students and their cumulative study hours."""
    # Ensure only admin can access this page
    if 'username' not in session or session['username'] != 'ADMIN':
        return "Unauthorized", 403

    # Filter by month and student name if selected
    selected_month = request.form.get('month', None)
    selected_student = request.form.get('student_name', None)

    # Prepare sorted list of students by registered name and then by subject
    sorted_students = []
    for username, months in student_data.items():
        if selected_student and users_db[username]['registered_name'] != selected_student.upper():
            continue  # Skip if the selected student doesn't match

        for month, subjects in months.items():
            if selected_month is None or format_month_year(selected_month) == month:
                for subject, hours in subjects.items():
                    sorted_students.append((users_db[username]['registered_name'], subject, hours, month))

    sorted_students = sorted(sorted_students, key=lambda x: (x[0], x[3], x[1]))  # Sort by registered name, month, then by subject

    # Calculate total hours per student for the selected filters
    total_hours_per_student = {}
    for username, months in student_data.items():
        registered_name = users_db[username]['registered_name']
        if selected_student and registered_name != selected_student.upper():
            continue  # Skip if the selected student doesn't match

        for month, subjects in months.items():
            if selected_month is None or format_month_year(selected_month) == month:
                if registered_name not in total_hours_per_student:
                    total_hours_per_student[registered_name] = sum(subjects.values())
                else:
                    total_hours_per_student[registered_name] += sum(subjects.values())

    return render_template('admin.html', sorted_students=sorted_students, total_hours_per_student=total_hours_per_student, selected_month=selected_month, selected_student=selected_student)

@app.route("/user-dashboard", methods=["GET", "POST"])
def user_dashboard():
    """Display the dashboard for the logged-in user (non-admin)."""
    if 'username' not in session or session['username'] == 'ADMIN':
        return redirect(url_for('login'))  # Only non-admin users can access their own dashboard
    
    student_name = session['username']
    registered_name = users_db[student_name]['registered_name']

    # Get selected month for filtering
    selected_month = request.form.get('month', None)
    
    # Retrieve the logged-in user's study data
    user_study_data = []
    if student_name in student_data:
        for month, subjects in student_data[student_name].items():
            if selected_month is None or format_month_year(selected_month) == month:
                for subject, hours in subjects.items():
                    user_study_data.append((registered_name, subject, hours, month))

    user_study_data = sorted(user_study_data, key=lambda x: (x[3], x[1]))  # Sort by month, then by subject

    # Enumerate (index) the data
    indexed_user_study_data = list(enumerate(user_study_data, start=1))

    # Calculate total hours per month
    total_hours_per_month = {}
    if student_name in student_data:
        for month, subjects in student_data[student_name].items():
            if selected_month is None or format_month_year(selected_month) == month:
                total_hours_per_month[month] = sum(subjects.values())

    # Enumerate (index) total hours
    indexed_total_hours_per_month = list(enumerate(total_hours_per_month.items(), start=1))

    return render_template(
        'user_dashboard.html', 
        user_study_data=indexed_user_study_data, 
        total_hours_per_month=indexed_total_hours_per_month, 
        selected_month=selected_month, 
        registered_name=registered_name,
        format_month_year=format_month_year  # Pass the function to the template
    )

if __name__ == "__main__":
    app.run(debug=True)