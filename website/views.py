from flask import Blueprint, render_template, request, flash
import os

from openai import OpenAI

views = Blueprint("views", __name__)

@views.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        prompt = request.form.get("prompt")

        if len(prompt) >= 2:
            flash("Template generated!", category="success")

        else:
            flash("Prompt must be at least two characters", category="error")

    return render_template("home.html")

@views.route("/templates", methods=["GET", "POST"])
def templates():
    return render_template("templates.html")