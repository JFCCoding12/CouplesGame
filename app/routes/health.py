from flask import Blueprint, render_template
health_bp=Blueprint("health",__name__)
@health_bp.get("/health")
def health(): return {"status":"ok"}

@health_bp.route("/join/<code>")
def join_redirect(code):
    return render_template(
        "join.html",
        code=code
    )