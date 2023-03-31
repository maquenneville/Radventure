# -*- coding: utf-8 -*-
"""
Created on Sat Mar 25 23:34:21 2023

@author: marca
"""

from BookBuilderHelpers import *
import os
import concurrent.futures
import backoff

def generate_photo_with_backoff(*args, **kwargs):
    @backoff.on_exception(backoff.expo, Exception, max_tries=5)
    def wrapped_generate_photo():
        return generate_photo(*args, **kwargs)
    return wrapped_generate_photo()

def refine_draft_with_backoff(*args, **kwargs):
    @backoff.on_exception(backoff.expo, Exception, max_tries=5)
    def wrapped_refine_draft():
        return refine_draft(*args, **kwargs)
    return wrapped_refine_draft()

def main():
# =============================================================================
#     print("Welcome to Radventure, where anything is possible!\n")
#     print("What kind of story would you like to build?")
# 
#     genre = input("Enter the genre of your story: ")
#     target_audience = input("Enter the target audience age: ")
#     theme = input("Enter the theme of your story: ")
#     setting = input("Enter a setting for your story: ")
#     content_hint = input("Enter some additional details for your story: ")
#     twisted = False
#     
#     while True:
#         
#         twist_response = input("Do you want a twist in the story? (yes/no): ")
#     
#         if twist_response.lower() in ['yes', 'no']:
#             if twist_response == 'yes':
#                 twisted = True
#                 break
#             else:
#                 break
#         
#         else:
#             print("Please respond with yes or no.")
# =============================================================================
            
    genre = "uplifting"
    target_audience = "5 year olds"
    theme = "The importance of getting enough protein in your diet"
    setting = "a forest"
    content_hint = "The main characters are children who live in a cottage in the forest, Billy, Jonny, Sara and Beth."
    twisted = False
        

    print("\nCreating a prompt based on your ideas...")
    prompt = build_prompt(genre, target_audience, theme, setting, content_hint, twist=twisted)

    enhanced = enhance_build_prompt(prompt)
    print(enhanced)

    print("Coming up with cool, different plot ideas, and picking the best one...")
    outline, title = select_best_outline(enhanced)
    print(outline)

    print("Writing your story...")
    sections = build_first_draft(outline)
    if len(sections) == 0:
        print("Oops, got a little distracted, NOW I'm writing your story...")
        sections = build_first_draft(outline)
        
    print("Trimming the story down to make it less repetitive...")
        
    concise = process_story_sections(sections)

    print("Checking your story so it makes sense...")

    with concurrent.futures.ThreadPoolExecutor() as executor:
        photo_future = executor.submit(generate_photo_with_backoff, outline, title)
        refined_future = executor.submit(refine_draft_with_backoff, sections, title)

        description, photo_file = photo_future.result()
        refined_draft = refined_future.result()
    
    print("Printing your story...")
    output_path = f"{title.replace(' ', '_')}_storybook.pdf"
    create_finished_copy(photo_file, title, refined_draft, output_path)

    print(f"\nYour story '{title}' has been created and saved as '{output_path}'. Enjoy reading!")

if __name__ == '__main__':
    main()







