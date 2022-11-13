from functools import wraps
from app.models import *
from flask import render_template, request, redirect, session
from main import app, firebaseDb
import bcrypt
import json
from datetime import datetime


# ------------ Decorators ---------------
def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if session.get('username', None) is None:
            return redirect("/401")
        return func(*args, **kwargs)

    return wrapper


def role_required(role):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if session.get('role', None) != role:
                return redirect("/403")
            return func(*args, **kwargs)

        return wrapper

    return decorator


# ------------- Miscellaneous ---------------

@app.route('/403', methods=['GET'])
def no_permission():
    return render_template('403.html')


@app.route('/401', methods=['GET'])
def not_logged_in():
    return render_template('401.html')


@app.errorhandler(404)
def not_found():
    return render_template('404.html')


@app.errorhandler(500)
def internal_server_error():
    return render_template('500.html')


# -------------- Profile Related ----------------------

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        bytePwt = password.encode('utf-8')
        if user is None:
            return render_template('login.html', error='Username does not exist!')
        byteCheckPwt = str(user.password).encode('utf-8')
        check = bcrypt.checkpw(bytePwt, byteCheckPwt)
        if check:
            session['username'] = user.username
            userRole = UserRole.query.filter_by(user_id=user.id).first()
            role = Role.query.filter_by(id=userRole.role_id).first()
            session['role'] = role.name
            session['userId'] = user.id
            session['firstName'] = user.firstName
            return redirect('/redirect')
        else:
            return render_template('login.html', error='Username or Password Incorrect!')


@app.route('/redirect', methods=['GET'])
def redirector():
    role = session.get('role', None)
    if role is None:
        return redirect('/')
    elif role == 'admin':
        return redirect('/admin')
    elif role == 'teacher':
        return redirect('/teacher')
    elif role == 'student':
        return redirect('/student')
    elif role == 'warden':
        return redirect('/warden')
    else:
        return 404


@app.route('/logout', methods=['GET'])
@login_required
def logout():
    del session['username']
    del session['role']
    return redirect('/')


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    role = session['role']
    firstName = session['firstName']
    userId = session['userId']
    user = User.query.filter_by(id=userId).first()
    if request.method == 'GET':
        return render_template('profile.html', firstName=firstName, user=user, role=role)
    if request.method == 'POST':
        username = request.form.get('username')
        if user.username != username:
            check = User.query.filter_by(username=username).first()
            if check is not None:
                return render_template('profile.html', firstName=firstName, user=user, role=role,
                                       error='Username already exist!')
        firstname = request.form.get('firstName')
        lastname = request.form.get('lastName')
        pno = request.form.get('pno')
        email = request.form.get('email')
        user.username = username
        user.firstName = firstname
        user.lastName = lastname
        user.pno = pno
        user.email = email
        session['firstName'] = firstname
        db.session.commit()
        return render_template('profile.html', firstName=firstName, user=user, role=role, info='Profile edited!')


@app.route('/profile/changePassword', methods=['GET', 'POST'])
@login_required
def changePassword():
    firstName = session['firstName']
    role = session['role']
    if request.method == 'GET':
        return render_template('change_password.html', firstName=firstName, role=role)
    if request.method == 'POST':
        userId = session['userId']
        currentPassword = request.form.get('currentPassword')
        user = User.query.filter_by(id=userId).first()
        bytePwt = currentPassword.encode('utf-8')
        byteCheckPwt = str(user.password).encode('utf-8')
        check = bcrypt.checkpw(bytePwt, byteCheckPwt)
        if not check:
            return render_template('change_password.html', firstName=firstName, role=role, error='Wrong Password!')
        newPassword = request.form.get('newPassword')
        bytePwd = newPassword.encode('utf-8')
        salt = bcrypt.gensalt()
        hashedPwd = bcrypt.hashpw(bytePwd, salt)
        user.password = hashedPwd
        db.session.commit()
        return render_template('profile.html', firstName=firstName, user=user, role=role, info='Password Changed!')


# ----------------- Admin ----------------------

@app.route('/admin', methods=['GET'])
@login_required
@role_required('admin')
def admin():
    firstName = session['firstName']
    notices = firebaseDb.child('noticeBoard').get()
    rawNoticeList = notices.val()
    if rawNoticeList is None:
        return render_template('admin_dash.html', firstName=firstName, empty=True)
    noticeList = []
    for i, j in rawNoticeList.items():
        k = json.loads(j)
        k['key'] = i
        noticeList.append(k)
    noticeList.reverse()
    return render_template('admin_dash.html', firstName=firstName, noticeList=noticeList)


@app.route('/notice', methods=['GET'])
@login_required
@role_required('admin')
def notice():
    firstName = session['firstName']
    return render_template('create_notice.html', firstName=firstName)


@app.route('/notice/create', methods=['POST'])
@login_required
@role_required('admin')
def create_notice():
    firstName = session['firstName']
    title = request.form.get('title')
    description = request.form.get('description')
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    data = {
        "title": title,
        "description": description,
        "creation_date_time": dt_string,
        "updated_date_time": None
    }
    firebaseDb.child('noticeBoard').push(json.dumps(data))
    return render_template('notice_success.html', task='Created', firstName=firstName)


@app.route('/notice/edit/<string:key>', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def edit_notice(key):
    firstName = session['firstName']
    rawData1 = firebaseDb.child('noticeBoard').child(key).get()
    rawData2 = rawData1.val()
    data = json.loads(rawData2)
    data['key'] = key
    if request.method == 'GET':
        return render_template('edit_notice.html', firstName=firstName, notice=data)
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        newData = {
            "title": title,
            "description": description,
            "creation_date_time": data['creation_date_time'],
            "updated_date_time": dt_string
        }
        firebaseDb.child('noticeBoard').child(key).set(json.dumps(newData))
        return render_template('notice_success.html', task='Edited', firstName=firstName)


@app.route('/notice/delete/<string:key>', methods=['GET'])
@login_required
@role_required('admin')
def deleteNotice(key):
    firebaseDb.child('noticeBoard').child(key).remove()
    firstName = session['firstName']
    return render_template('notice_success.html', task='Deleted', firstName=firstName)


@app.route('/user', methods=['GET'])
@login_required
@role_required('admin')
def userPage():
    firstName = session['firstName']
    return render_template('user.html', firstName=firstName)


@app.route('/user/add', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def addUser():
    firstName = session['firstName']
    if request.method == 'GET':
        courses = Course.query.all()
        return render_template('add_user.html', firstName=firstName, courses=courses)
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        firstname = request.form.get('firstName')
        lastname = request.form.get('lastName')
        pno = request.form.get('pno')
        email = request.form.get('email')
        role = request.form.get('role')
        check = User.query.filter_by(username=username).first()
        if check is not None:
            return render_template('add_user.html', firstName=firstName, error='Username already exist!')
        roleObj = Role.query.filter_by(name=role).first()
        bytePwd = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashedPwd = bcrypt.hashpw(bytePwd, salt)
        user = User(username=username, password=hashedPwd, firstName=firstname, lastName=lastname, pno=pno, email=email)
        db.session.add(user)
        db.session.commit()
        userRole = UserRole(user_id=user.id, role_id=roleObj.id)
        db.session.add(userRole)
        db.session.commit()
        if role == 'student':
            courses = request.form.getlist('course')
            print(courses)
            for course in courses:
                print(course)
                enrollment = Enrollment(student_id=user.id, course_id=int(course))
                db.session.add(enrollment)
                db.session.commit()
        return render_template('user_success.html', task='Created', firstName=firstName)


@app.route('/user/modify', methods=['POST'])
@login_required
@role_required('admin')
def modifyUser():
    firstName = session['firstName']
    username = request.form.get('username')
    user = User.query.filter_by(username=username).first()
    if user is None:
        return render_template('user.html', firstName=firstName, error='Invalid Username!')
    userRole = UserRole.query.filter_by(user_id=user.id).first()
    role = Role.query.filter_by(id=userRole.role_id).first()
    enrollments = Enrollment.query.filter_by(student_id=user.id).all()
    enrollmentList = []
    for enrollment in enrollments:
        enrollmentList.append(enrollment.course_id)
    courses = Course.query.all()
    return render_template('modify_user.html', user=user, firstName=firstName, role=role.name, courses=courses,
                           enrollments=enrollmentList)


@app.route('/user/edit/<int:user_id>', methods=['POST'])
@login_required
@role_required('admin')
def editUser(user_id):
    firstName = session['firstName']
    username = request.form.get('username')
    firstname = request.form.get('firstName')
    lastname = request.form.get('lastName')
    pno = request.form.get('pno')
    email = request.form.get('email')
    role = request.form.get('role')
    user = User.query.filter_by(id=user_id).first()
    flag = False
    if username != user.username:
        check = User.query.filter_by(username=username).first()
        if check is not None:
            flag = True
        else:
            user.username = username
    user.firstName = firstname
    user.lastName = lastname
    user.pno = pno
    user.email = email
    if flag:
        return render_template('modify_user.html', user=user, role=role, firstName=firstName,
                               error='Username already exist!')
    roleObj = Role.query.filter_by(name=role).first()
    userRole = UserRole.query.filter_by(user_id=user_id).first()
    userRole.role_id = roleObj.id
    db.session.commit()
    enrollments = Enrollment.query.filter_by(student_id=user_id).all()
    for enrollment in enrollments:
        db.session.delete(enrollment)
    if role == 'student':
        courses = request.form.getlist('course')
        print(courses)
        for course in courses:
            print(course)
            enrollment = Enrollment(student_id=user.id, course_id=int(course))
            db.session.add(enrollment)
            db.session.commit()
    return render_template('user_success.html', task="Edited", firstName=firstName)


@app.route('/user/delete/<int:user_id>', methods=['GET'])
@login_required
@role_required('admin')
def deleteUser(user_id):
    firstName = session['firstName']
    enrollments = Enrollment.query.filter_by(student_id=user_id).all()
    for enrollment in enrollments:
        db.session.delete(enrollment)
    instructors = Instructor.query.filter_by(teacher_id=user_id).all()
    for instructor in instructors:
        db.session.delete(instructor)
    leaves = Leave.query.filter_by(student_id=user_id).all()
    for leave in leaves:
        db.session.delete(leave)
    userRole = UserRole.query.filter_by(user_id=user_id).first()
    db.session.delete(userRole)
    user = User.query.filter_by(id=user_id).first()
    db.session.delete(user)
    db.session.commit()
    return render_template('user_success.html', task='Deleted', firstName=firstName)


@app.route('/admin/course', methods=['GET'])
@login_required
@role_required('admin')
def adminCourse():
    firstName = session['firstName']
    return render_template('admin_course.html', firstName=firstName)


@app.route('/admin/course/add', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def addCourse():
    firstName = session['firstName']
    teachers = []
    if request.method == 'GET':
        role = Role.query.filter_by(name='Teacher').first()
        userRoles = UserRole.query.filter_by(role_id=role.id).all()
        for userRole in userRoles:
            user = User.query.filter_by(id=userRole.user_id).first()
            teacher = {
                'id': user.id,
                'name': user.firstName + ' ' + user.lastName
            }
            teachers.append(teacher)
        return render_template('add_course.html', firstName=firstName, teachers=teachers)
    if request.method == 'POST':
        code = request.form.get('code')
        name = request.form.get('name')
        description = request.form.get('description')
        teacher = request.form.get('teacher')
        check = Course.query.filter_by(code=code).first()
        if check is not None:
            return render_template('add_course.html', firstName=firstName, teachers=teachers,
                                   error='Course Code already exist!')
        course = Course(code=code, name=name, description=description)
        db.session.add(course)
        db.session.commit()
        instructor = Instructor(teacher_id=teacher, course_id=course.id)
        db.session.add(instructor)
        db.session.commit()
        return render_template('course_success.html', task='Created', firstName=firstName)


@app.route('/admin/course/modify', methods=['POST'])
@login_required
@role_required('admin')
def adminCourseModify():
    firstName = session['firstName']
    code = request.form.get('code')
    course = Course.query.filter_by(code=code).first()
    if course is None:
        return render_template('admin_course.html', firstName=firstName, error='Course does not exist!')
    teachers = []
    role = Role.query.filter_by(name='Teacher').first()
    userRoles = UserRole.query.filter_by(role_id=role.id).all()
    for userRole in userRoles:
        user = User.query.filter_by(id=userRole.user_id).first()
        teacher = {
            'id': user.id,
            'name': user.firstName + ' ' + user.lastName
        }
        teachers.append(teacher)
    instructor = Instructor.query.filter_by(course_id=course.id).first()
    instructorId = instructor.teacher_id
    return render_template('modify_course.html', firstName=firstName, course=course, teachers=teachers,
                           instructorId=instructorId)


# ----------------- Teacher --------------------


@app.route('/teacher', methods=['GET'])
@login_required
@role_required('teacher')
def teacher_dash():
    firstName = session['firstName']
    notices = firebaseDb.child('noticeBoard').get()
    rawNoticeList = notices.val()
    if rawNoticeList is None:
        return render_template('teacher_dash.html', firstName=firstName, empty=True)
    noticeList = []
    for i in rawNoticeList.values():
        j = json.loads(i)
        noticeList.append(j)
    noticeList.reverse()
    return render_template('teacher_dash.html', firstName=firstName, noticeList=noticeList)


@app.route('/teacher/course', methods=['GET'])
@login_required
@role_required('teacher')
def teacher_course():
    if request.method == 'GET':
        user_id = session['userId']
        firstName = session['firstName']
        instructors = Instructor.query.filter_by(teacher_id=user_id).all()
        courses = []
        for instructor in instructors:
            course = Course.query.filter_by(id=instructor.course_id).first()
            courses.append(course)
        return render_template('teacher_course_view.html', courses=courses, firstName=firstName)


@app.route('/teacher/course/<int:courseId>', methods=['GET'])
@login_required
@role_required('teacher')
def teacherCoursePortal(courseId):
    course = Course.query.filter_by(id=courseId).first()
    firstName = session['firstName']
    material = firebaseDb.child('courseMaterial').child(course.code).get()
    rawMaterialList = material.val()
    if rawMaterialList is None:
        return render_template('course_teacher_dash.html', course=course, firstName=firstName, empty=True)
    materialList = []
    for i, j in rawMaterialList.items():
        k = json.loads(j)
        k['key'] = i
        materialList.append(k)
    materialList.reverse()
    return render_template('course_teacher_dash.html', course=course, firstName=firstName, materialList=materialList)


@app.route('/teacher/course/<int:courseId>/material', methods=['GET'])
@login_required
@role_required('teacher')
def courseMaterial(courseId):
    firstName = session['firstName']
    course = Course.query.filter_by(id=courseId).first()
    return render_template('course_material_create.html', firstName=firstName, course=course)


@app.route('/teacher/course/<int:courseId>/material/create', methods=['POST'])
@login_required
@role_required('teacher')
def createCourseMaterial(courseId):
    firstName = session['firstName']
    course = Course.query.filter_by(id=courseId).first()
    title = request.form.get('title')
    description = request.form.get('description')
    link = request.form.get('link')
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    data = {
        "title": title,
        "description": description,
        "creation_date_time": dt_string,
        "updated_date_time": None,
        'link': link
    }
    firebaseDb.child('courseMaterial').child(course.code).push(json.dumps(data))
    return render_template('course_material_success.html', task='Created', firstName=firstName, course=course)


@app.route('/teacher/course/<int:courseId>/material/edit/<string:key>', methods=['GET', 'POST'])
@login_required
@role_required('teacher')
def editCourseMaterial(courseId, key):
    firstName = session['firstName']
    course = Course.query.filter_by(id=courseId).first()
    rawData1 = firebaseDb.child('courseMaterial').child(course.code).child(key).get()
    rawData2 = rawData1.val()
    data = json.loads(rawData2)
    data['key'] = key
    if request.method == 'GET':
        return render_template('course_material_edit.html', firstName=firstName, material=data, course=course)
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        link = request.form.get('link')
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        newData = {
            "title": title,
            "description": description,
            "creation_date_time": data['creation_date_time'],
            "updated_date_time": dt_string,
            'link': link
        }
        firebaseDb.child('courseMaterial').child(course.code).child(key).set(json.dumps(newData))
        return render_template('course_material_success.html', task='Edited', firstName=firstName, course=course)


@app.route('/teacher/course/<int:courseId>/material/delete/<string:key>', methods=['GET', 'POST'])
@login_required
@role_required('teacher')
def courseMaterialDelete(courseId, key):
    course = Course.query.filter_by(id=courseId).first()
    firebaseDb.child('courseMaterial').child(course.code).child(key).remove()
    firstName = session['firstName']
    return render_template('course_material_success.html', task='Deleted', firstName=firstName, course=course)


@app.route('/teacher/course/<int:courseId>/assignment', methods=['GET'])
@login_required
@role_required('teacher')
def teacherAssignment(courseId):
    firstName = session['firstName']
    course = Course.query.filter_by(id=courseId).first()
    assignments = firebaseDb.child('assignments').child(course.code).get()
    rawAssignmentList = assignments.val()
    if rawAssignmentList is None:
        return render_template('course_assignment.html', course=course, firstName=firstName, empty=True)
    assignmentList = []
    for i, j in rawAssignmentList.items():
        k = json.loads(j)
        k['key'] = i
        assignmentList.append(k)
    assignmentList.reverse()
    return render_template('course_assignment.html', firstName=firstName, course=course, assignments=assignmentList)


@app.route('/teacher/course/<int:courseId>/assignment/create', methods=['GET', 'POST'])
@login_required
@role_required('teacher')
def teacherAssignmentCreate(courseId):
    firstName = session['firstName']
    course = Course.query.filter_by(id=courseId).first()
    if request.method == 'GET':
        return render_template('create_assignment.html', firstName=firstName, course=course)
    if request.method == 'POST':
        title = request.form.get('title')
        deadline = request.form.get('deadline')
        description = request.form.get('description')
        link = request.form.get('link')
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y")
        data = {
            'title': title,
            'createdOn': dt_string,
            'editedOn': None,
            'deadline': deadline,
            'description': description,
            'link': link
        }
        firebaseDb.child('assignments').child(course.code).push(json.dumps(data))
        return render_template('teacher_assignment_success.html', task='Created', firstName=firstName, course=course)


@app.route('/teacher/course/<int:courseId>/assignment/<string:key>', methods=['GET'])
@login_required
@role_required('teacher')
def assignmentPage(courseId, key):
    firstName = session['firstName']
    course = Course.query.filter_by(id=courseId).first()
    rawData1 = firebaseDb.child('assignments').child(course.code).child(key).get()
    rawData2 = rawData1.val()
    data = json.loads(rawData2)
    data['key'] = key
    return render_template('course_assignment_modify.html', firstName=firstName, course=course, assignment=data)


@app.route('/teacher/course/<int:courseId>/assignment/<string:key>/submissions')
@login_required
@role_required('teacher')
def assignment(courseId, key):
    firstName = session['firstName']
    course = Course.query.filter_by(id=courseId).first()
    submissions = firebaseDb.child('submissions').child(course.code).child(key).get()
    rawSubmissionList = submissions.val()
    if rawSubmissionList is None:
        return render_template('course_assignment_submission_view.html', course=course, firstName=firstName, empty=True)
    submissionList = []
    for i, j in rawSubmissionList.items():
        k = json.loads(j)
        k['key'] = i
        submissionList.append(k)
    submissionList.reverse()
    return render_template('course_assignment_submission_view.html', course=course, firstName=firstName,
                           submissions=submissionList)


@app.route('/teacher/course/<int:courseId>/assignment/<string:key>/edit', methods=['POST'])
@login_required
@role_required('teacher')
def assignmentEdit(courseId, key):
    firstName = session['firstName']
    course = Course.query.filter_by(id=courseId).first()
    rawData1 = firebaseDb.child('assignments').child(course.code).child(key).get()
    rawData2 = rawData1.val()
    data = json.loads(rawData2)
    title = request.form.get('title')
    deadline = request.form.get('deadline')
    description = request.form.get('description')
    link = request.form.get('link')
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y")
    newData = {
        'title': title,
        'createdOn': data['createdOn'],
        'editedOn': dt_string,
        'deadline': deadline,
        'description': description,
        'link': link
    }
    firebaseDb.child('assignments').child(course.code).child(key).set(json.dumps(newData))
    return render_template('teacher_assignment_success.html', task='Edited', firstName=firstName, course=course)


@app.route('/teacher/course/<int:courseId>/assignment/<string:key>/delete', methods=['GET'])
@login_required
@role_required('teacher')
def assignmentDelete(courseId, key):
    firstName = session['firstName']
    course = Course.query.filter_by(id=courseId).first()
    firebaseDb.child('assignments').child(course.code).child(key).remove()
    return render_template('teacher_assignment_success.html', task='Deleted', firstName=firstName, course=course)


# ----------------- Student --------------------

@app.route('/student', methods=['GET'])
@login_required
@role_required('student')
def student_dash():
    firstName = session['firstName']
    notices = firebaseDb.child('noticeBoard').get()
    rawNoticeList = notices.val()
    if rawNoticeList is None:
        return render_template('admin_dash.html', firstName=firstName, empty=True)
    noticeList = []
    for i in rawNoticeList.values():
        j = json.loads(i)
        noticeList.append(j)
    noticeList.reverse()
    return render_template('student_dash.html', firstName=firstName, noticeList=noticeList)


@app.route('/leave', methods=['GET'])
@login_required
@role_required('student')
def student_leave_applied():
    firstName = session['firstName']
    applied_leave = Leave.query.filter_by(student_id=session['userId']).all()
    appliedList = []
    for leave in applied_leave:
        appliedList.append(leave)
    appliedList.reverse()
    return render_template('leave_applications.html', firstName=firstName, appliedList=appliedList)


@app.route('/leave/apply', methods=['GET', 'POST'])
@login_required
@role_required('student')
def student_leave():
    firstName = session['firstName']
    if request.method == 'GET':
        return render_template('leave.html', firstName=firstName)
    if request.method == 'POST':
        user_id = session['userId']
        checkin = request.form.get('checkin')
        checkout = request.form.get('checkout')
        reason = request.form.get('reason')
        new_leave = Leave(from_date=checkout, to_date=checkin, student_id=user_id, reason=reason, status='Pending')
        db.session.add(new_leave)
        db.session.commit()
        return render_template('leave_applied.html', firstName=firstName)


@app.route('/student/course', methods=['GET'])
@login_required
@role_required('student')
def student_course():
    user_id = session['userId']
    firstName = session['firstName']
    enrollments = Enrollment.query.filter_by(student_id=user_id).all()
    courseList = []
    for enrollment in enrollments:
        course = Course.query.filter_by(id=enrollment.course_id).first()
        courseList.append(course)
    return render_template('student_course_view.html', courses=courseList, firstName=firstName)


@app.route('/student/course/<string:courseId>', methods=['GET'])
@login_required
@role_required('student')
def student_assignment(courseId):
    course = Course.query.filter_by(id=courseId).first()
    firstName = session['firstName']
    material = firebaseDb.child('courseMaterial').child(course.code).get()
    rawMaterialList = material.val()
    if rawMaterialList is None:
        return render_template('course_student_dash.html', course=course, firstName=firstName, empty=True)
    materialList = []
    for i in rawMaterialList.values():
        materialList.append(json.loads(i))
    materialList.reverse()
    return render_template('course_student_dash.html', course=course, firstName=firstName, materialList=materialList)


@app.route('/student/course/<int:courseId>/assignment', methods=['GET'])
@login_required
@role_required('student')
def studentAssignment(courseId):
    firstName = session['firstName']
    course = Course.query.filter_by(id=courseId).first()
    assignments = firebaseDb.child('assignments').child(course.code).get()
    rawAssignmentList = assignments.val()
    if rawAssignmentList is None:
        return render_template('student_course_assignment.html', course=course, firstName=firstName, empty=True)
    assignmentList = []
    now = datetime.now()
    dt_string = now.strftime("%Y-%m-%d")
    for i, j in rawAssignmentList.items():
        k = json.loads(j)
        k['key'] = i
        if k['deadline'] < dt_string:
            k['deadlinePassed'] = True
        assignmentList.append(k)
    assignmentList.reverse()
    info = session.get('info', None)
    if info is not None:
        del session['info']
    return render_template('student_course_assignment.html', firstName=firstName, course=course,
                           assignments=assignmentList, info=info)


@app.route('/student/course/<int:courseId>/assignment/submit/<string:key>', methods=['POST'])
@login_required
@role_required('student')
def assignmentSubmit(courseId, key):
    course = Course.query.filter_by(id=courseId).first()
    link = request.form.get('link')
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y")
    userId = session['userId']
    user = User.query.filter_by(id=userId).first()
    data = {
        'name': user.firstName + ' ' + user.lastName,
        'submittedOn': dt_string,
        'link': link
    }
    firebaseDb.child('submissions').child(course.code).child(key).child(userId).set(json.dumps(data))
    session['info'] = 'Assignment Submitted Successfully!'
    return redirect('/student/course/' + str(courseId) + '/assignment')


# ----------------- Warden ---------------------
@app.route('/warden', methods=['GET'])
@login_required
@role_required('warden')
def warden():
    firstName = session['firstName']
    notices = firebaseDb.child('noticeBoard').get()
    rawNoticeList = notices.val()
    if rawNoticeList is None:
        return render_template('teacher_dash.html', firstName=firstName, empty=True)
    noticeList = []
    for i in rawNoticeList.values():
        j = json.loads(i)
        noticeList.append(j)
    noticeList.reverse()
    return render_template('warden_dash.html', firstName=firstName, noticeList=noticeList)


@app.route('/warden/leave', methods=['GET'])
@login_required
@role_required('warden')
def warden_leave():
    if request.method == 'GET':
        firstName = session['firstName']
        leaveList = Leave.query.filter_by(status='Pending').all()
        if not leaveList:
            return render_template('warden_leave.html', firstName=firstName, empty=True)
        leave_dict = dict()
        for leave in leaveList:
            student = User.query.filter_by(id=leave.student_id).first()
            leave_id = leave.id
            leave_dict[leave_id] = student.firstName + " " + student.lastName
        return render_template('warden_leave.html', firstName=firstName, leave_dict=leave_dict, leaveList=leaveList)


@app.route('/warden/leave/accept/<int:leave_id>', methods=['GET'])
@login_required
@role_required('warden')
def leave_accept(leave_id):
    target_leave = Leave.query.filter_by(id=leave_id).first()
    target_leave.status = 'Accepted'
    db.session.commit()
    return redirect('/warden/leave')


@app.route('/warden/leave/reject/<int:leave_id>', methods=['GET'])
@login_required
@role_required('warden')
def leave_reject(leave_id):
    target_leave = Leave.query.filter_by(id=leave_id).first()
    target_leave.status = 'Rejected'
    db.session.commit()
    return redirect('/warden/leave')
