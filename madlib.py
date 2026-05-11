def get_input(word_type: str):
    user_input: str = input(f"enter a {word_type}:")
    return user_input


noun1 = get_input("noun")
adjective1 = get_input("adjective")
verb1 = get_input("verb1")
noun2 = get_input("noun2")
verb2 = get_input("verb2")

story = f"""
One sunny morning, I found a {adjective1} {noun1} outside my house.
At first, I thought it was completely normal, but then it suddenly started to {verb1}.

I was so surprised that I ran toward the nearest {noun2} to hide.
But before I could reach it, the {noun2} began to {verb2} all by itself.

Everyone around me stopped and stared in shock.
Nobody could believe that a {adjective1} {noun1} and a {noun2} could create so much chaos in one day.

In the end, I decided this was the strangest adventure of my life.
From that day on, I never looked at a {noun1} or a {noun2} the same way again.
"""

print(story)