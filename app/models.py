from flask_login import UserMixin
from sqlalchemy.sql import func
from . import db

class User(db.model):
    id = db.Column(db.Integer, primary_key=True, auto_increment=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    firstName = db.Column(db.String, nullable=False)
    lastName = db.Column(db.String)
    pno = db.Column(db.String)
    email = db.Column(db.String)


class Role(db.model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)


class Role_user(db.model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))


class Course(db.model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String, unique=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String)


class Enrollment(db.model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))


class Instructor(db.model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))


class Leave(db.model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    from_date = db.Column(db.DateTime, nullable=False)
    to_date = db.Column(db.DateTime, nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    reason = db.Column(db.String)
    status = db.Column(db.String)
