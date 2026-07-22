from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from app.models import User

web_bp = Blueprint("web", __name__)

@web_bp.get("/login")
def login():
    return render_template("login.html")

@web_bp.post("/login")
def login_post():
    email = request.form.get("email")
    password = request.form.get("password")

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        flash("Invalid email or password.")
        return redirect(url_for("web.login"))

    login_user(user)

    if user.is_admin:
        return redirect(url_for("admin_web.dashboard"))

    return redirect("/")

@web_bp.post("/logout")
def logout():
    logout_user()
    return redirect(url_for("web.login"))