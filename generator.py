from openai import OpenAI
client = OpenAI()

message_history = []
user_input = input("design prompt > ")

message_history.append({"role": "system", "content": "You are a website designer and web developer. You create website templates in HTML and CSS based on user prompts. You will only print a heading with the format ###filename###, replacing filename with the chosen filename including the extension. Do not use backticks to format responses in HTML/CSS."})
message_history.append({"role": "user", "content": f"Create a website template for {user_input}."})

completion = client.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=message_history
)

# print(completion)

reply_content = completion.choices[0].message.content.strip()
print(reply_content)

message_history.append({"role": "assistant", "content": reply_content})
