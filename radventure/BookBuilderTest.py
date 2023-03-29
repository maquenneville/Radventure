# -*- coding: utf-8 -*-
"""
Created on Sat Mar 25 23:34:21 2023

@author: marca
"""

from BookBuilderHelpers import *
import os

def main():
    print("Welcome to Radventure, where anything is possible!\n")
    print("What kind of story would you like to build?")

    genre = input("Enter the genre of your story: ")
    target_audience = input("Enter the target audience age: ")
    theme = input("Enter the theme of your story: ")
    content_hint = input("Enter some additional details for your story: ")

    print("\nCreating a prompt based on your ideas...")
    prompt = build_prompt(genre, target_audience, theme, content_hint)

    enhanced = enhance_prompt(prompt)

    print("Coming up with cool, different plot ideas, and picking the best one...")
    outline, title = select_best_outline(enhanced)

    print("Writing your story...")
    sections = build_first_draft(outline)

    print("Checking and editing your story so it makes sense...")
    refined = refine_draft(sections, title)

    # Save the story to a txt file
    file_name = f"{title.replace(' ', '_')}.txt"
    with open(file_name, 'w', encoding='utf-8') as f:
        f.write(refined)

    print(f"\nYour story '{title}' has been created and saved as '{file_name}'. Enjoy reading!")

if __name__ == '__main__':
    main()
