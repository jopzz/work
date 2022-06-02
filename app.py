
from enum import unique
import random
from flask import Flask, render_template, g, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(50))
    email = db.Column(db.String(50), unique=True)
    otp = db.Column(db.Integer)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    complete = db.Column(db.Boolean)

db.create_all()

app.secret_key = 'somesecretkeythatonlyishouldknow'

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        user = User(username=username, password=password, email=email)
        db.session.add(user)
        db.session.commit()

        return redirect(url_for("login"))        

    else:
        return render_template('register.html')

@app.route('/forgot', methods=['GET', 'POST'])
def forgotPassword():

    if request.method == 'POST':
        email = request.form['email']

        user = User.query.filter_by(email=email).first()
        user.otp = random.randint(1000,9999)
        print('OTP SEND ' + str(user.otp))

        # Send OTP to email logic

        db.session.commit()

        return render_template('forgot-password-otp.html', email=email)
    else:
        return render_template('forgot-password.html')


@app.route('/change-password', methods=['POST'])
def changePassword():
    otp = int(request.form['otp'])
    email = request.form['email']
    new_password = request.form['password']

    user = User.query.filter_by(email=email).first()
    if user is not None and user.otp == otp:
        user.password = new_password
        user.otp = None
        db.session.commit()

        return redirect('login')

    return redirect(url_for("forgotPassword"))    

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session.pop('user_id', None)

        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        print(user is not None and user.password == password)
        if user is not None and user.password == password:
            session['user_id'] = user.id
            return redirect(url_for('home'))

        return redirect(url_for('login'))

    return render_template('login.html')

@app.route("/")
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    todo_list = Todo.query.all()
    return render_template("base.html", todo_list=todo_list)

@app.route("/logout")
def logout():
    session['user_id'] = None
    g.user = None
    return redirect(url_for('login'))


@app.route("/add", methods=["POST"])
def add():
    title = request.form.get("title")
    new_todo = Todo(title=title, complete=False)
    db.session.add(new_todo)
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/update/<int:todo_id>")
def update(todo_id):
    todo = Todo.query.filter_by(id=todo_id).first()
    todo.complete = not todo.complete
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/edit/<int:todo_id>", methods=["POST"])
def edit(todo_id):
    title = request.form.get("title")
    todo = Todo.query.filter_by(id=todo_id).first()
    todo.title = title
    db.session.commit()
    return redirect(url_for("home"))

@app.route("/delete/<int:todo_id>")
def delete(todo_id):
    todo = Todo.query.filter_by(id=todo_id).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for("home"))

if __name__ == "__main__":
   
    app.run(debug=True)