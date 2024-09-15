from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_migrate import Migrate

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Configure the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database and Flask-Migrate
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Create a model for tasks
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    completed = db.Column(db.Boolean, default=False)
    start_date = db.Column(db.Date, nullable=True, default=datetime.utcnow)
    due_date = db.Column(db.Date, nullable=True)
    priority = db.Column(db.String(50), nullable=False, default='Medium')

    def __repr__(self):
        return f'<Task {self.id}>'

# Route for displaying and adding tasks
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        task_content = request.form.get('task')
        task_description = request.form.get('description')
        task_due_date = request.form.get('due_date')
        task_priority = request.form.get('priority')

        new_task = Task(content=task_content, description=task_description, due_date=task_due_date, priority=task_priority)

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect(url_for('index'))
        except Exception as e:
            print(f"Error adding task: {e}")
            return 'There was an issue adding your task.'

    filter_by = request.args.get('filter_by', 'start_date')
    search = request.args.get('search', '')

    valid_columns = ['start_date', 'due_date', 'priority', 'completed']
    if filter_by not in valid_columns:
        filter_by = 'start_date'

    tasks_query = Task.query

    if search:
        tasks_query = tasks_query.filter(Task.content.ilike(f'%{search}%'))

    tasks = tasks_query.order_by(db.asc(getattr(Task, filter_by))).all()

    return render_template('index.html', tasks=tasks)

# Route for deleting a task
@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    task_to_delete = Task.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect(url_for('index'))
    except:
        return 'There was a problem deleting that task.'

# Route for completing or un-completing a task
@app.route('/complete/<int:id>', methods=['POST'])
def complete(id):
    task = Task.query.get_or_404(id)
    task.completed = not task.completed

    try:
        db.session.commit()
        return redirect(url_for('index'))
    except:
        return 'There was an issue updating the task.'

# Route for updating (edit) a task
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_task(id):
    task = Task.query.get_or_404(id)

    if request.method == 'POST':
        task.content = request.form['task']
        task.description = request.form['description']

        db.session.commit()
        return redirect('/')

    return render_template('edit.html', task=task)

@app.route('/update_due_date/<int:id>', methods=['POST'])
def update_due_date(id):
    task = Task.query.get_or_404(id)
    task.due_date = datetime.strptime(request.form['due_date'], '%Y-%m-%d').date()
    
    try:
        db.session.commit()
        return redirect(url_for('index'))
    except Exception as e:
        print(f"Error updating due date: {e}")
        return 'There was an issue updating the due date.'

@app.route('/update_priority/<int:id>', methods=['POST'])
def update_priority(id):
    task = Task.query.get_or_404(id)
    task.priority = request.form['priority']
    
    try:
        db.session.commit()
        return redirect(url_for('index'))
    except Exception as e:
        print(f"Error updating priority: {e}")
        return 'There was an issue updating the priority.'

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/dashboard')
def dashboard():
    total_tasks = Task.query.count()
    completed_tasks = Task.query.filter_by(completed=True).count()
    upcoming_tasks = Task.query.filter(Task.due_date >= datetime.now()).count()
    
    return render_template('dashboard.html', total_tasks=total_tasks, 
                           completed_tasks=completed_tasks, 
                           upcoming_tasks=upcoming_tasks)

if __name__ == '__main__':
    app.run(debug=True)
