from flask import Blueprint, Response, render_template, request, redirect, url_for
from .models import Template
from . import db
import os

from openai import OpenAI
from typing import List

views = Blueprint("views", __name__)

USE_FULL_MESSAGE_HISTORY = False # Set to True for way better website update context (but more costly and has a token limit).

@views.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        prompt = request.form.get("prompt")

        if not prompt or is_invalid(prompt):
            return render_template("home.html", templates=Template.query.all(),
                                   message="Invalid or inappropriate prompt. Please try again.")

        reply_content, message_history = generate_response(prompt)
        save_template(prompt, reply_content, message_history)
        
        return redirect(url_for("views.get_template", id=Template.query.order_by(Template.id.desc()).first().id))

    return render_template("home.html", templates=Template.query.all(), message="")

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

    response = completion.choices[0].message.content.strip()
    message_history.append({"role": "assistant", "content": response})
    return response, message_history

def update_response(new_prompt: str, message_history: List[str]) -> str:
    client = OpenAI()

    if len(message_history) < 3:
        raise Exception("Invalid message history!")
    
    simplified_message_history = message_history[:1].append(message_history[-1])

    full_prompt = {"role": "user", "content": f"Update the website template with the following information: {new_prompt}. Reply with the entire HTML file with the updated changes."}
    simplified_message_history.append(full_prompt)
    message_history.append(full_prompt)

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=message_history if USE_FULL_MESSAGE_HISTORY else simplified_message_history
    )

    response = completion.choices[0].message.content.strip()
    message_history.append({"role": "assistant", "content": response})
    return response, message_history

def save_template(prompt: str, html: str, message_history: List[str]) -> None:
    # Save template in the generated database
    new_template = Template(prompt=prompt, html=html, message_history=message_history)
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
    
    if request.method == "POST":
        if request.form.get("delete"):
            db.session.delete(template)
            db.session.commit()
            return redirect(url_for("views.home"))
        elif request.form.get("download") and not request.form.get("prompt"):
            return Response(
                template.html,
                mimetype='text/html',
                headers={'Content-disposition': 'attachment; filename=index.html'}
            )
        else:
            prompt = request.form.get("prompt")
            if not prompt or is_invalid(prompt):
                return render_template("template.html", template=template.html)

            template.html, template.message_history = update_response(prompt, template.message_history)
            print(template.message_history)
            db.session.commit()
        
    return render_template("template.html", template=template.html)
        
@views.route("/templates/", methods=["GET", "POST"])
def display_templates():
    return redirect(url_for("views.home") + "#templates")