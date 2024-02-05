from flask import Blueprint, render_template, request, flash, render_template_string, redirect, url_for
from .models import Template
from . import db
import os

from openai import OpenAI

views = Blueprint("views", __name__)

@views.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        prompt = request.form.get("prompt")

        if len(prompt) >= 2:
            reply_content = generate_response(prompt)
            save_template(prompt, reply_content)
            
            return redirect(url_for("views.get_template", id=Template.query.order_by(Template.id.desc()).first().id))
        else:
            flash("Prompt must be at least two characters", category="error")

    return render_template("home.html")

def generate_response(prompt: str) -> str:
    client = OpenAI()

    message_history = []

    system_prompt = ("You are a website designer and web developer. You create website templates solely in HTML " +
                    "based on user prompts. You must create exactly one HTML file with embedded CSS styling (no CSS file). " +
                    "Do not use backticks to format responses in HTML. Make the website specific to the prompt by prepopulating " +
                    "with relevant text, emojis, and stylized buttons. Do not use external images and do not use Lorem ipsum. " +
                    "Make the websites lively and unique and relevant to the type of prompt.")

    message_history.append({"role": "system", "content": system_prompt})
    message_history.append({"role": "user", "content": f"Create a website template for: {prompt}."})

    completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=message_history
    )

    return completion.choices[0].message.content.strip()

def save_template(prompt: str, html: str) -> None:
    # Save template in the generated database
    new_template = Template(prompt=prompt, html=html)
    db.session.add(new_template)
    db.session.commit()

@views.route("/templates", methods=["GET", "POST"])
def templates():
    return render_template("templates.html", templates=Template.query.all())

@views.route("/templates/<int:id>", methods=["GET", "POST"])
def get_template(id):
    template = Template.query.filter_by(id=id).first()
    if not template:
        return "No template with that id", 404

    return render_template_string(template.html)