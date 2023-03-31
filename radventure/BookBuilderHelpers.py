# -*- coding: utf-8 -*-
"""
Created on Sat Mar 25 23:04:07 2023

@author: marca
"""

import openai
from openai.error import RateLimitError, InvalidRequestError
import requests
import time
import re
import os
import configparser
import sys
from transformers import GPT2TokenizerFast
import requests
from PIL import Image as PIL_Image
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import inch


tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")


def get_openai_api_key():
    if getattr(sys, "frozen", False):
        # If the script is running as a PyInstaller-generated .exe
        exe_dir = os.path.dirname(sys.executable)
    else:
        # If the script is running as a regular Python script
        exe_dir = os.path.dirname(os.path.realpath(__file__))

    config = configparser.ConfigParser()
    config_path = os.path.join(exe_dir, "config.ini")
    config.read(config_path)

    openai_api_key = config.get("OpenAI", "api_key")
    return openai_api_key


# Set up the OpenAI API client
openai.api_key = get_openai_api_key()


def generate_response(
    messages, temperature=0.5, n=1, max_tokens=4000, frequency_penalty=0
):

    model_engine = "gpt-3.5-turbo"

    # Calculate the number of tokens in the messages
    tokens_used = sum([len(tokenizer.encode(msg["content"])) for msg in messages])
    tokens_available = 4096 - tokens_used

    # Adjust max_tokens to not exceed the available tokens
    max_tokens = min(max_tokens, (tokens_available - 100))

    # Reduce max_tokens further if the total tokens exceed the model limit
    if tokens_used + max_tokens > 4096:
        max_tokens = 4096 - tokens_used - 10

    if max_tokens < 1:
        max_tokens = 1

    # Generate a response
    max_retries = 10
    retries = 0
    while True:
        if retries < max_retries:
            try:
                completion = openai.ChatCompletion.create(
                    model=model_engine,
                    messages=messages,
                    n=n,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    frequency_penalty=frequency_penalty,
                )
                break
            except (RateLimitError, KeyboardInterrupt):
                time.sleep(60)
                retries += 1
                print("Server overloaded, retrying in a minute")
                continue
        else:
            print("Failed to generate prompt after max retries")
            return
    response = completion.choices[0].message.content
    return response


def build_prompt(genre, target_audience, theme, setting, content_hint, twist=False):

    if twist:
        prompt = f"Write a {genre} children's book targeted at {target_audience} about {theme}.  It takes place in {setting}. Include a surprise twist at some point in the story."

    else:
        prompt = f"Write a {genre} children's book targeted at {target_audience} about {theme}.  It takes place in {setting}. {content_hint}"

    return prompt


def enhance_build_prompt(prompt):
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {
            "role": "user",
            "content": f"I want you to become my Prompt Optimizer. Your goal is to help me craft the best possible prompt for my needs. The prompt will be used by you, ChatGPT.  You will be improving a prompt for creating a children's story.  Your improvements must not change the setting, genre, theme, narrator, characters, or any twists involved.  What improvements can and should be made to this prompt: {prompt}",
        },
    ]

    suggestions = generate_response(messages, temperature=0.2, max_tokens=2000)
    messages.append({"role": "assistant", "content": suggestions})
    messages.append(
        {
            "role": "user",
            "content": "Using your suggestions, improve the prompt for generating content with GPT.  Just generate the revised prompt, no need for explanatory text.",
        }
    )
    improved_prompt = generate_response(messages, temperature=0.2, max_tokens=2000)
    return improved_prompt


def enhance_prompt(prompt):
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {
            "role": "user",
            "content": f"I want you to become my Prompt Optimizer. Your goal is to help me craft the best possible prompt for my needs. The prompt will be used by you, ChatGPT.  What improvements can and should be made to this prompt: {prompt}",
        },
    ]

    suggestions = generate_response(messages, temperature=0.2, max_tokens=1000)
    messages.append({"role": "assistant", "content": suggestions})
    messages.append(
        {
            "role": "user",
            "content": "Using your suggestions, improve the prompt for generating content with GPT.  Just generate the revised prompt, no need for explanatory text.",
        }
    )
    improved_prompt = generate_response(messages, temperature=0.2, max_tokens=1000)
    return improved_prompt


def select_best_outline(enhanced_prompt):
    model_engine = "gpt-3.5-turbo"

    def match_best_outline(ranking_response, outlines):
        # Regex to find a title in quotes or after "Title:"
        title_pattern = r'(?:"([^"]+)"|Title:\s*(.*)|(?:\d+\.\s+(.*)(?:\n|$)))'
        top_title_regex = re.compile(title_pattern, re.MULTILINE)

        # Find the top-ranked title in the ranking_response
        top_title_match = top_title_regex.search(ranking_response)
        if top_title_match:
            top_title = (
                top_title_match.group(1)
                or top_title_match.group(2)
                or top_title_match.group(3)
            )
        else:
            return None, None

        # Find the outline with the top-ranked title
        for outline in outlines:
            if top_title in outline:
                return outline, top_title

        return None, None

    def enhance_outline(outline):
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": f"I want you to become my Children's Book Outline Editor.  Your job is to take an outline, and check it to ensure it isn't redundant, and that each section is unique, and flows well with the others. Tell me some ways this outline can be improved: \n{outline}",
            },
        ]

        suggestions = generate_response(messages, temperature=0.2, max_tokens=1000)
        messages.append({"role": "assistant", "content": suggestions})

        messages.append(
            {
                "role": "user",
                "content": "Implement the suggested changes, and generate the revised outline. Only generate the outline, no need to give any explanatory text.",
            }
        )
        enhanced_outline = generate_response(messages, temperature=0.2)

        return enhanced_outline

    # Generate 5 different outlines using the enhanced prompt
    outlines_completion = openai.ChatCompletion.create(
        model=model_engine,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": f"You are an incredibly talented children's book author.  You know how to weave a story together in a way that is engaging and fun to read.  You keep things fresh, exciting, and ensure that your stories aren't repetitive.\nCreate an outline for a children's book based on this prompt: '{enhanced_prompt}'",
            },
        ],
        n=5,
        temperature=1.2,
    )

    outlines = [choice.message.content for choice in outlines_completion.choices]

    # Initialize messages with the ranking request
    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant, who's job is ranking outlines for children's books.",
        },
        {
            "role": "user",
            "content": "Rank the following children's story outlines from 1 to 5, with 1 being the best and 5 being the least preferred:",
        },
    ]

    # Iterate through outlines and ask GPT to rank each one
    for outline in outlines:
        messages.append({"role": "user", "content": outline})

    messages.append(
        {
            "role": "user",
            "content": "Now, provide the rankings.  Remember to simply rank them in order, do not explain your reasoning.  Include the outline titles in your rankings.",
        }
    )
    rankings = generate_response(messages, temperature=0.2, max_tokens=1000)

    best, title = match_best_outline(rankings, outlines)
    best = enhance_outline(best)

    return best, title


def build_first_draft(outline):
    model_engine = "gpt-3.5-turbo"

    # Initialize the list to store the generated sections
    sections = []

    # Split the outline into separate sections
    section_pattern = r"(?<=\n\n)[\s\S]*?(?=\n\n)"
    section_prompts = re.findall(section_pattern, outline)

    # Initialize the messages with the assistant's role
    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant who writes children's book sections based on provided outlines.",
        },
        {
            "role": "user",
            "content": "You are an extremely talented and creative children's book author.  Together, we are going to write a children's book, step by step.",
        },
    ]

    # Iterate through the section prompts and generate content for each section
    for prompt in section_prompts[1:]:

        messages.append(
            {
                "role": "user",
                "content": f"Write a section for a children's book based on this part of the outline, ensuring that the wording is not repetitive: '{prompt}'",
            }
        )
        section_content = generate_response(
            messages, temperature=0.7, max_tokens=2000, frequency_penalty=0.8
        )
        messages.append({"role": "assistant", "content": section_content})
        sections.append(section_content)

    return sections


def check_and_combine_sections(prev_section, cur_section):
    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant that combines repetitive sections.",
        },
        {
            "role": "user",
            "content": "You are a very talented editor, who takes two sequential sections of a book and check to ensure they are not redundant, and that they're both necessary to the plot of the story. If they aren't, you combine them into one section that is not redundant, is concise, yet maintains the tone, characters and feeling of the section.",
        },
        {
            "role": "assistant",
            "content": "Of course, what sections can I help you with today?",
        },
        {"role": "user", "content": f"Previous section: {prev_section}"},
        {"role": "user", "content": f"Current section: {cur_section}"},
        {
            "role": "user",
            "content": "Are these sections repetitive? If so, make the first word of your response 'Yesindeedy', and then combine them into a single unique section.",
        },
    ]

    response = generate_response(messages, temperature=0.2, max_tokens=500)

    # Check if the response indicates that the sections are repetitive
    if "yesindeedy" in response.lower():
        return response.strip()
    else:
        return prev_section, cur_section


def process_story_sections(sections):
    processed_sections = []
    prev_section = sections[0]

    for i in range(1, len(sections)):
        cur_section = sections[i]
        result = check_and_combine_sections(prev_section, cur_section)

        if isinstance(result, tuple):
            # If the result is a tuple, add the prev_section to the processed_sections list
            # and update the prev_section to be the cur_section for the next iteration
            processed_sections.append(result[0])
            prev_section = result[1]
        else:
            # If the result is a single combined section, update the prev_section to be the combined section
            prev_section = result

    # Add the final section to the processed_sections list
    processed_sections.append(prev_section)

    return processed_sections


def continuity_check_prompt_first(prev_section, curr_section):
    return f"Does the following section maintain continuity and flow well with the previous section, and is not repetitive compared to the previous section? Respond with only a single word, true or false.  Previous section: '{prev_section}'. Current section: '{curr_section}'"


def continuity_check_prompt(cur_section):
    return f"Does the following section maintain continuity and flow well with the previous section? Respond with only a single word, true or false. Current section: '{cur_section}'"


def refine_draft(book_sections, title):
    refined_sections = [
        book_sections[0]
    ]  # Add the first section as it doesn't need to be checked for continuity
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {
            "role": "user",
            "content": "You are an extremely talented editor of children's books.  Your specialty is ensuring that the story maintains cohesion, continuity and flows well together, while not being redundant or repetitive.  We're going to ensure that this children's story maintains continuity, step by step.",
        },
        {
            "role": "user",
            "content": "This is the first section: {refined_sections[0]}.",
        },
    ]

    for i in range(1, len(book_sections)):
        prev_section = book_sections[i - 1]
        curr_section = book_sections[i]

        # Check if the current section maintains continuity with the previous section
        messages.append(
            {"role": "user", "content": continuity_check_prompt(curr_section)}
        )
        response = generate_response(messages, temperature=0.2, max_tokens=5)

        while response.lower() not in ("true", "false", "true.", "false."):
            messages.append(
                {
                    "role": "user",
                    "content": "Please respond with only one word, 'true' or 'false'.",
                }
            )
            response = generate_response(messages, temperature=0.2, max_tokens=5)
            print(response)

        # If the response is false, ask GPT to fix the section for better continuity and flow
        if response.lower() == "false":
            messages.append(
                {
                    "role": "user",
                    "content": f"Please fix this section so that it maintains continuity and flows well with the previous section. Current section: '{curr_section}'",
                }
            )
            fixed_section = generate_response(
                messages, temperature=0.2, max_tokens=2000
            )
            refined_sections.append(fixed_section)
            messages.append({"role": "assistant", "content": fixed_section})
        else:
            refined_sections.append(curr_section)
            messages.append({"role": "assistant", "content": response})

    # Check for continuity between the first and last sections
    first_section = refined_sections[0]
    last_section = refined_sections[-1]

    messages.append(
        {
            "role": "user",
            "content": continuity_check_prompt_first(first_section, last_section),
        }
    )
    response = generate_response(messages, temperature=0.2, max_tokens=5)

    while response.lower() not in ("true", "false", "true.", "false."):
        messages.append(
            {
                "role": "user",
                "content": "Please respond with only one word, 'true' or 'false'.",
            }
        )
        response = generate_response(messages, temperature=0.2, max_tokens=5)
        print(response)
    if response.lower() == "false":
        return "Got lost"
    else:
        return "\n\n".join(refined_sections)


def generate_photo(outline, title):

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {
            "role": "user",
            "content": "You are my Photo Prompt Creator.  You take book outlines, and create a one sentence prompt to be used by openai.Image.create().  The prompt will describe a picture of a scene from the book, in a cartoon/animated style.  A cartoon picture you might use on the cover of the children's book.  Have it match the tone and feeling of the outline.",
        },
        {
            "role": "assistant",
            "content": "Great! Please provide me with the book outline and any specific instructions or preferences you have for the tone and feeling of the prompt.",
        },
        {"role": "user", "content": outline},
    ]

    picture_prompt = generate_response(messages, temperature=0.2, max_tokens=150)
    picture_prompt = enhance_prompt(picture_prompt)

    response = openai.Image.create(prompt=picture_prompt, n=1, size="512x512")
    image_url = response["data"][0]["url"]

    response = requests.get(image_url)

    image_file = f"{title.replace(' ', '_')}_image.png"
    img = PIL_Image.open(BytesIO(response.content))
    img.save(image_file, "PNG")
    return picture_prompt, image_file


def create_finished_copy(image_path, title, story_text, output_path):
    doc = SimpleDocTemplate(output_path, pagesize=letter)

    # Create a list to store the flowables (elements) in the document
    elements = []

    # Add the image
    image = Image(image_path)
    image.drawHeight = 200
    image.drawWidth = 200
    image.hAlign = "CENTER"
    elements.append(image)

    # Add some space
    elements.append(Spacer(1, 12))

    # Add the title
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        name="TitleStyle", parent=styles["Title"], fontSize=24, alignment=TA_CENTER
    )
    title_paragraph = Paragraph(title, style=title_style)
    elements.append(title_paragraph)

    # Add some space
    elements.append(Spacer(1, 12))

    # Add the story
    story_style = ParagraphStyle(
        name="StoryStyle", parent=styles["Normal"], fontSize=14
    )
    story_paragraphs = story_text.split("\n")
    for paragraph in story_paragraphs:
        elements.append(Paragraph(paragraph, style=story_style))
        elements.append(Spacer(1, 12))

    # Build the document
    doc.build(elements)


# Example usage:
# create_finished_copy('path/to/image.jpg', 'Story Title', 'Story content', 'output.pdf')
