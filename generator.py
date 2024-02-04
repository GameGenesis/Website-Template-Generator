import os
from openai import OpenAI
client = OpenAI()

message_history = []
user_input = input("design prompt > ")

message_history.append({"role": "system", "content": "You are a website designer and web developer. You create website templates in HTML and CSS based on user prompts. You will only print a heading with the format ###filename###, replacing filename with the chosen filename including the extension. You must create exactly one HTML file and one CSS file. This means you will have exactly two headings. Do not use backticks to format responses in HTML/CSS."})
message_history.append({"role": "user", "content": f"Create a website template for {user_input}."})

completion = client.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=message_history
)

# print(completion)

reply_content = completion.choices[0].message.content.strip()
# print(reply_content)

message_history.append({"role": "assistant", "content": reply_content})

# ------------------- Managing Content String ----------------------

split_content = reply_content.split("###")
print(split_content)
current_content_index = 1

html_filename = "index.html"

for i in range(len(split_content)):
    if 6 <= len(split_content[current_content_index]) <= 261 and ".html" in split_content[current_content_index]:
        html_filename = split_content[current_content_index].strip()
    else:
        current_content_index += 1

current_content_index += 1
html_content = split_content[current_content_index].strip()

current_content_index += 1
css_filename = "styles.css"

for i in range(len(split_content) - current_content_index - 1):
    if 5 <= len(split_content[current_content_index]) <= 260 and ".css" in split_content[current_content_index]:
        css_filename = split_content[current_content_index].strip()
    else:
        current_content_index += 1

current_content_index += 1
css_content = split_content[current_content_index].strip()

# --------------- IO ---------------------

template_dir = "templates"
html_path = os.path.join(template_dir, html_filename)
css_path = os.path.join(template_dir, css_filename)

with open(html_path, 'w') as f:
    f.write(html_content)

with open(css_path, 'w') as f:
    f.write(css_content)