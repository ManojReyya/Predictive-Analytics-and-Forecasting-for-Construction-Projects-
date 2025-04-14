from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin, current_user
import os
import pandas as pd
from datetime import datetime
import joblib
import numpy as np

app = Flask(__name__)
app.secret_key = "your-secret-key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///construction.db'
app.config['UPLOAD_FOLDER'] = 'uploads'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# mind save the data in sql
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(256), nullable=False)
    profession = db.Column(db.String(100), nullable=True)
    gender = db.Column(db.String(50), nullable=True)
    is_admin = db.Column(db.Boolean, default=False)
    is_blocked = db.Column(db.Boolean, default=False)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(50), default='Planned')

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    name = db.Column(db.String(200))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    status = db.Column(db.String(50), default='Pending')
    project = db.relationship('Project', backref='tasks')

class Progress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    completion_percentage = db.Column(db.Float, nullable=False)
    delay_days = db.Column(db.Integer, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    task = db.relationship('Task', backref='progress')


#secure auth
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
@app.route('/')
def home():
    return redirect(url_for('login'))
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        profession = request.form.get('profession')

        if User.query.filter_by(email=email).first():
            flash("Email already registered.", "error")
            return redirect(url_for('register'))

        is_first_user = User.query.count() == 0
        new_user = User(
            username=username,
            email=email,
            password=password,
            profession=profession,
            is_admin=is_first_user
        )
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful. Please login.", "success")
        return redirect(url_for('login'))
    return render_template('register.html')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            if user.is_blocked:
                flash("User is blocked.", "error")
                return redirect(url_for('login'))
            login_user(user)
            return redirect(url_for('index'))
        flash("Invalid credentials.", "error")
    return render_template('login.html')
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


#main dasshboard
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    if request.method == 'POST':
        if 'project_name' in request.form:
            if not current_user.is_admin:  # Only allow Admin users to add projects
                flash("You are not authorized to add a project.", "error")
                return redirect(url_for('index'))

            name = request.form['project_name']
            start = request.form['start_date']
            end = request.form['end_date']

            new_project = Project(
                name=name,
                start_date=datetime.strptime(start, '%Y-%m-%d'),
                end_date=datetime.strptime(end, '%Y-%m-%d')
            )
            db.session.add(new_project)
            db.session.commit()
            flash("Project added successfully!", "success")
        elif 'file' in request.files:
            if not current_user.is_admin:  # Only allow Admin users to import projects from files
                flash("You are not authorized to import a project.", "error")
                return redirect(url_for('index'))

            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = file.filename
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                import_project_file(file_path)
                flash("Project imported from file!", "success")
            else:
                flash("Only .xlsx and .csv files are allowed!", "error")

        return redirect(url_for('index'))
    projects = Project.query.all()
    return render_template("index.html", projects=projects)


#admin work
@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin_panel():
    if not current_user.is_admin:
        flash("Unauthorized Access.", "error")
        return redirect(url_for('index'))
    users = User.query.all()
    return render_template('adminpanel.html', users=users)
@app.route('/make_admin/<int:user_id>')
@login_required
def make_admin(user_id):
    if current_user.is_admin:
        user = User.query.get(user_id)
        user.is_admin = True
        db.session.commit()
    return redirect(url_for('admin_panel'))
@app.route('/remove_admin/<int:user_id>')
@login_required
def remove_admin(user_id):
    if current_user.is_admin:
        user = User.query.get(user_id)
        user.is_admin = False
        db.session.commit()
    return redirect(url_for('admin_panel'))
@app.route('/block_user/<int:user_id>')
@login_required
def block_user(user_id):
    if current_user.is_admin:
        user = User.query.get(user_id)
        user.is_blocked = True
        db.session.commit()
    return redirect(url_for('admin_panel'))
@app.route('/unblock_user/<int:user_id>')
@login_required
def unblock_user(user_id):
    if current_user.is_admin:
        user = User.query.get(user_id)
        user.is_blocked = False
        db.session.commit()
    return redirect(url_for('admin_panel'))
@app.route('/delete_user/<int:user_id>')
@login_required
def delete_user(user_id):
    if current_user.is_admin:
        user = User.query.get(user_id)
        db.session.delete(user)
        db.session.commit()
    return redirect(url_for('admin_panel'))


#task management
@app.route('/task/<int:task_id>/progress', methods=['GET', 'POST'])
@login_required
def add_progress(task_id):
    task = Task.query.get_or_404(task_id)
    if request.method == 'POST':
        completion_percentage = request.form['completion_percentage']
        delay_days = request.form.get('delay_days')
        notes = request.form.get('notes')
        date = datetime.strptime(request.form['date'], '%Y-%m-%d')
        new_progress = Progress(
            task_id=task.id,
            date=date,
            completion_percentage=float(completion_percentage),
            delay_days=int(delay_days) if delay_days else None,
            notes=notes
        )
        db.session.add(new_progress)
        task.status = "In Progress" if float(completion_percentage) < 100 else "Completed"
        db.session.commit()
        update_project_status(task.project)
        flash("Progress added successfully!", "success")
        return redirect(url_for('index'))
    return render_template('add_progress.html', task=task)
@app.route('/project/<int:project_id>/add-task-inline', methods=['POST'])
@login_required
def add_task_inline(project_id):
    if not current_user.is_admin:  
        flash("You are not authorized to add a task.", "error")
        return redirect(url_for('index'))

    project = Project.query.get_or_404(project_id)
    task_name = request.form['task_name']
    start = request.form['task_start_date']
    end = request.form['task_end_date']

    task = Task(
        project_id=project.id,
        name=task_name,
        start_date=datetime.strptime(start, '%Y-%m-%d'),
        end_date=datetime.strptime(end, '%Y-%m-%d')
    )
    db.session.add(task)
    db.session.commit()
    flash(f"Task '{task_name}' added to project '{project.name}'", "success")
    return redirect(url_for('index'))
@app.route('/delete_project/<int:project_id>', methods=['POST'])
@login_required
def delete_project(project_id):
    if not current_user.is_admin:
        flash("You are not authorized to delete projects.", "error")
        return redirect(url_for('index'))
    project = Project.query.get_or_404(project_id)
    for task in project.tasks:
        db.session.delete(task)
    try:
        db.session.delete(project)
        db.session.commit()
        flash("Project deleted successfully.", "success")
    except Exception as e:
        db.session.rollback()  
        flash(f"Error deleting project: {str(e)}", "error")
    return redirect(url_for('index'))
@app.route('/delete_task/<int:task_id>', methods=['POST'])
@login_required
def delete_task(task_id):
    if not current_user.is_admin:
        flash("You are not authorized to delete tasks.", "error")
        return redirect(url_for('index'))
    task = Task.query.get_or_404(task_id)
    for progress in task.progress:
        db.session.delete(progress)
    try:
        db.session.delete(task)
        db.session.commit()
        flash("Sub-task deleted successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting sub-task: {str(e)}", "error")
    return redirect(url_for('index'))
@app.route('/project/<int:project_id>/report')
@login_required
def project_report(project_id):
    project = Project.query.get_or_404(project_id)
    tasks = Task.query.filter_by(project_id=project.id).all()
    progress_data = []
    for task in tasks:
        for prog in task.progress:
            progress_data.append({
                'task_name': task.name,
                'date': prog.date.strftime('%Y-%m-%d'),
                'completion_percentage': prog.completion_percentage,
                'delay_days': prog.delay_days,
                'notes': prog.notes
            })
    return render_template('analytics.html', project=project, progress_data=progress_data)


# machine learning models to predictions
model_completion = joblib.load('models/model_predicted_completion.pkl')
model_workers = joblib.load('models/model_additional_workers.pkl')
model_materials = joblib.load('models/model_additional_materials.pkl')

@app.route('/core', methods=['GET', 'POST'])
@login_required
def core():
    prediction = None

    if request.method == 'POST':
        try:
            work_progress = float(request.form['work_progress'])
            worker_availability = int(request.form['worker_availability'])
            material_availability = float(request.form['material_availability'])
            equipment_availability = float(request.form['equipment_availability'])
            delays = int(request.form['delays'])
            resource_shortage = int(request.form['resource_shortage'])
            budget_overrun = float(request.form['budget_overrun'])

            features = np.array([[work_progress, worker_availability, material_availability,
                                  equipment_availability, delays, resource_shortage, budget_overrun]])

            predicted_days = model_completion.predict(features)[0]
            predicted_workers = model_workers.predict(features)[0]
            predicted_materials = model_materials.predict(features)[0]
            prediction = {
                'predicted_days': round(predicted_days),
                'predicted_workers': int(predicted_workers),
                'predicted_materials': round(predicted_materials, 2)
            }
        except Exception as e:
            prediction = {'error': str(e)}

    return render_template('core.html', prediction=prediction)


# importing project file in csv or xlsx
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['xlsx', 'csv']

def import_project_file(path):
    ext = path.rsplit('.', 1)[1].lower()
    try:
        df = pd.read_excel(path) if ext == 'xlsx' else pd.read_csv(path)
        project_name = df['Project Name'][0]
        start_date = datetime.strptime(str(df['Project Start Date'][0]), "%Y-%m-%d")
        end_date = datetime.strptime(str(df['Project End Date'][0]), "%Y-%m-%d")

        new_project = Project(name=project_name, start_date=start_date, end_date=end_date)
        db.session.add(new_project)
        db.session.commit()

        for _, row in df.iterrows():
            task = Task(
                project_id=new_project.id,
                name=row['Task Name'],
                start_date=datetime.strptime(str(row['Task Start Date']), "%Y-%m-%d"),
                end_date=datetime.strptime(str(row['Task End Date']), "%Y-%m-%d")
            )
            db.session.add(task)

        db.session.commit()
    except Exception as e:
        flash(f"Error importing file: {str(e)}", "error")

def update_project_status(project):
    statuses = [task.status for task in project.tasks]
    if all(s == 'Completed' for s in statuses):
        project.status = 'Completed'
    elif any(s == 'In Progress' for s in statuses):
        project.status = 'In Progress'
    else:
        project.status = 'Planned'
    db.session.commit()




if __name__ == '__main__':
    os.makedirs('uploads', exist_ok=True)
    with app.app_context():
        db.create_all()
    app.run(debug=True)
