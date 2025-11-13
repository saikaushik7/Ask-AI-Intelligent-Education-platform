from flask import Blueprint

quiz_bp = Blueprint(
    "quiz_bp",
    __name__,
    template_folder="templates"
)

from quiz import routes_quiz  # noqa: E402
