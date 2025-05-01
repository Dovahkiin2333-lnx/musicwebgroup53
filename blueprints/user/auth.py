from flask import Blueprint, render_template, jsonify, redirect, url_for, session
from extensions.exts import mail, db
from sqlalchemy import select
from flask_mail import Message
from flask import request
from forms.auth_form import RegisterForm, LoginForm
from models.models import UserModel, EmailCaptchaModel, Student, SearchIndexModel, PlaylistModel
from werkzeug.security import generate_password_hash, check_password_hash
import string
import random
from flask_login import login_user

bp = Blueprint("auth", __name__)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("auth/login.html")
    else:
        form = LoginForm(request.form)
        if form.validate():
            email = form.email.data
            password = form.password.data
            user = db.session.scalars(
                select(UserModel).where(UserModel.email == email).limit(1)
            ).first()
            if not user:
                print("email is not in database")
                return redirect(url_for("auth.login"))
            if check_password_hash(user.password, password):
                login_user(user)
                return redirect("/")
            else:
                print("wrong pw")
                return redirect(url_for("auth.login"))
        else:
            print(form.errors)
            return redirect(url_for("auth.login"))


@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("auth/register.html")
    else:
        form = RegisterForm(request.form)
        if form.validate():
            email = form.email.data
            username = form.username.data
            password = form.password.data

            s_name = None
            student_id = None
            role = "user"

            if email.endswith("@liverpool.ac.uk"):
                role = "student"
                student = db.session.scalar(
                    select(Student).where(Student.email == email).limit(1)
                )
                if student:
                    s_name = student.s_name
                    student_id = student.s_id

            user = UserModel(
                email=email,
                username=username,
                password=generate_password_hash(password),
                role=role,
                s_name=s_name,
                student_id=student_id,
            )

            db.session.add(user)
            db.session.commit()



            search_entry = SearchIndexModel(
            content_type="user",
            content_id=user.id,
            title=user.username,
            search_content=f"{user.username}"
            )
            db.session.add(search_entry)
            db.session.commit()

            collection = PlaylistModel.query.filter_by(
            user_id=user.id,
            title="My Collection"
            ).first()

            if not collection:
                my_collection = PlaylistModel(
                user_id = user.id,
                title = "My Collection"
            )
            db.session.add(my_collection)
            db.session.commit()
            
            return redirect(url_for("auth.login"))
        else:
            print(form.errors)
            return redirect(url_for("auth.register"))


@bp.route("/captcha/email")
def get_email_captcha():
    email = request.args.get("email")
    source = string.digits * 4
    captcha = random.sample(source, 4)
    captcha = "".join(captcha)
    message = Message(
        subject="Email Verification Code",
        recipients=[email],
        body=f"Your Verification Code is：{captcha} Do not tell others, do not send me junk emails",
    )
    mail.send(message)
    email_captcha = EmailCaptchaModel(email=email, captcha=captcha)
    db.session.add(email_captcha)
    db.session.commit()
    return jsonify({"code": 200, "message": "", "data": None})


@bp.route("/logout")
def logout():
    session.clear()
    return redirect("/")
