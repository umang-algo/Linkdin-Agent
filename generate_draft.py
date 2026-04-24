import os
import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

user_input = """Which future do we choose?

Today, our phones and browsers are crowded with apps—
each solving a small problem,
each demanding attention, context, and time.

Over the years, “productivity” has quietly turned into fragmentation.

With ChatOS, we’re exploring a simpler future.

A space where you don’t switch between tools.
A space where you don’t manage apps.
A space where you just… talk.

ChatOS is our attempt to bring multiple business AI agents together into one place—so work, decisions, and actions happen through conversation, not clutter.

One chat. One interface. Many capabilities.

We’re currently building this product, learning as we go, and questioning many assumptions along the way. This post is part of sharing that journey—what we’re building, why we’re building it, and how we think interaction with software will evolve.

The future doesn’t need more apps.
It needs less friction.

Stay tuned !"""

prompt = f"""
Write a highly engaging, professional LinkedIn post based on the following input thoughts.
Include a catchy hook, 2-3 short paragraphs, and relevant hashtags.
Preserve the core message and the mention of ChatOS.
Make it sound authentic and insightful.
The output should JUST be the text of the post itself.

Input thoughts:
{user_input}
"""

response = openai.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": prompt}]
)
print(response.choices[0].message.content)
