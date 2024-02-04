from openai import OpenAI
client = OpenAI()

completion = client.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "system", "content": "You are a website designer and web developer. You create website templates in HTML and CSS based on user prompts."},
    {"role": "user", "content": "Create a website template for a bakery."}
  ]
)

print(completion)

reply_content = completion.choices[0].message.content
print(reply_content)