from .database import db


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    firstName = db.Column(db.String, nullable=False)
    lastName = db.Column(db.String)
    pno = db.Column(db.String)
    email = db.Column(db.String)
    roles = db.relationship('Role', secondary='user_role')
    enrollments = db.relationship('Course', secondary='enrollment')
    instructors = db.relationship('Course', secondary='instructor')
    leaves = db.relationship('Leave')


class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)


class UserRole(db.Model):
    __tablename__ = 'user_role'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    role_id = db.Column(db.Integer, db.ForeignKey(Role.id))


class Course(db.Model):
    __tablename__ = 'course'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String, unique=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String)


class Enrollment(db.Model):
    __tablename__ = 'enrollment'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))


class Instructor(db.Model):
    __tablename__ = 'instructor'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))


class Leave(db.Model):
    __tablename__ = 'leave'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    from_date = db.Column(db.DateTime, nullable=False)
    to_date = db.Column(db.DateTime, nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    reason = db.Column(db.String)
    status = db.Column(db.String)
