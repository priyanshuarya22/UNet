from main import app
from flask import render_template
from flask_security import login_required, roles_required


@app.route('/')
def index():
    return "<a href='/index'>Click Me</a>"


@app.route('/index', methods=['GET'])
@login_required
@roles_required('admin')
def admin_dash():
    return render_template("index.html")
