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

        if not prompt or is_invalid(prompt):
            return render_template("index.html", templates=Template.query.all(),
                                   message="Invalid or inappropriate prompt. Please try again.")

        reply_content = generate_response(prompt)
        save_template(prompt, reply_content)
        
        return redirect(url_for("views.get_template", id=Template.query.order_by(Template.id.desc()).first().id))

    return render_template("index.html", templates=Template.query.all(), message="")

def generate_response(prompt: str) -> str:
    client = OpenAI()

    message_history = []

    system_prompt = ("You are a website designer and web developer. You create website templates solely in HTML " +
                    "based on user prompts. You must create exactly one HTML file with embedded CSS styling (no CSS file). " +
                    "Do not use backticks to format responses in HTML. Make the website specific to the prompt by prepopulating " +
                    "with relevant text, emojis, and stylized buttons. Do not reference image files - if you want to use images, " +
                    "use images from Unsplash or use placeholders. Do not use Lorem ipsum, use customized text. " +
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

def is_invalid(prompt: str) -> bool:
    stripped_prompt = prompt.replace(" ", "").lower()
    blacklist_path = os.path.join(os.getcwd(), "website", "static", "blacklist")
    whitelist_path = os.path.join(os.getcwd(), "website", "static", "whitelist")

    with open(blacklist_path, "rb") as blf:
        blacklist = blf.read().decode("unicode_escape").splitlines()

    with open(whitelist_path, "rb") as wlf:
        whitelist = wlf.read().decode("unicode_escape").splitlines()

    for bl_phrase in blacklist:
        stripper_bl_phrase = bl_phrase.replace(" ", "").lower()
        if stripper_bl_phrase not in stripped_prompt:
            continue

        whitelisted = False

        for wl_phrase in whitelist:
            stripper_wl_phrase = wl_phrase.replace(" ", "").lower()
            if stripper_bl_phrase not in stripped_prompt.replace(stripper_wl_phrase, ""):
                whitelisted = True
        
        if not whitelisted:
            return True
    
    return False

@views.route("/templates/<int:id>/", methods=["GET", "POST"])
def get_template(id):
    template = Template.query.filter_by(id=id).first()
    if not template:
        return "No template with that id", 404

    return render_template_string(template.html)

@views.route("/templates/", methods=["GET", "POST"])
def display_templates():
    return redirect(url_for("views.home") + "#templates")