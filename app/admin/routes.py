from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from app.extensions import db
from app.models import User
from flask_login import login_required, current_user

admin = Blueprint("admin", __name__, url_prefix="/admin")

@admin.route("/", methods = ["GET", "POST"])
@login_required
def dashboard():
    if  not current_user.id or not current_user.is_admin:
        flash("Unauthorized access!", "danger")
        return redirect(url_for("auth.login"))
    
    if request.method == "POST":
        user_id = request.form.get("id")
        
        if user_id:
            user = User.query.get(int(user_id))
            if user:
                db.session.delete(user)
                db.session.commit()

    accounts = User.query.all()
    return render_template("admin.html", accounts=accounts)