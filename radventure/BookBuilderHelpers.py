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

tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")

def get_openai_api_key():
    if getattr(sys, 'frozen', False):
        # If the script is running as a PyInstaller-generated .exe
        exe_dir = os.path.dirname(sys.executable)
    else:
        # If the script is running as a regular Python script
        exe_dir = os.path.dirname(os.path.realpath(__file__))

    config = configparser.ConfigParser()
    config_path = os.path.join(exe_dir, 'config.ini')
    config.read(config_path)

    openai_api_key = config.get('OpenAI', 'api_key')
    return openai_api_key


# Set up the OpenAI API client
openai.api_key = get_openai_api_key()


def generate_response(messages, temperature=0.5, n=1, max_tokens=4000):
    
    model_engine = "gpt-3.5-turbo"

    # Calculate the number of tokens in the messages
    tokens_used = sum([len(tokenizer.encode(msg["content"])) for msg in messages])
    tokens_available = 4096 - tokens_used

    # Adjust max_tokens to not exceed the available tokens
    max_tokens = min(max_tokens, (tokens_available - 100))
    
    # Reduce max_tokens further if the total tokens exceed the model limit
    if tokens_used + max_tokens > 4096:
        max_tokens = 4096 - tokens_used - 10

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
                    max_tokens=max_tokens
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



def build_prompt(genre, target_audience, theme, content_hint, narrator="omniscient"):
    prompt = f"Write a {genre} children's book targeted at {target_audience} about {theme}, using a {narrator} narrator. {content_hint}"
    return prompt


def enhance_prompt(prompt):
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": f"I want you to become my Prompt Optimizer. Your goal is to help me craft the best possible prompt for my needs. The prompt will be used by you, ChatGPT.  What improvements can and should be made to this prompt: {prompt}"}
    ]

    suggestions = generate_response(messages, temperature=0.2, max_tokens=2000)
    messages.append({"role": "assistant", "content": suggestions})
    messages.append({"role": "user", "content": "Using your suggestions, improve the prompt for generating content with GPT.  Just generate the revised prompt, no need for explanatory text."})
    improved_prompt = generate_response(messages, temperature=0.2, max_tokens=2000)
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
            top_title = top_title_match.group(1) or top_title_match.group(2) or top_title_match.group(3)
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
            {"role": "user", "content": f"I want you to become my Children's Book Outline Editor.  Your job is to take an outline, and check it to ensure it isn't redundant, and that each section is unique, and flows well with the others. Tell me some ways this outline can be improved: \n{outline}"}
        ]
    
        suggestions = generate_response(messages, temperature=0.2, max_tokens=1000)
        messages.append({"role": "assistant", "content": suggestions})
        
        messages.append({"role": "user", "content": "Implement the suggested changes, and generate the revised outline. Only generate the outline, no need to give any explanatory text."})
        enhanced_outline = generate_response(messages, temperature=0.2)
        
        return enhanced_outline


    # Generate 5 different outlines using the enhanced prompt
    outlines_completion = openai.ChatCompletion.create(
        model=model_engine,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"You are an incredibly talented children's book author.  You know how to weave a story together in a way that is engaging and fun to read.\nCreate an outline for a children's book based on this prompt: '{enhanced_prompt}'"}
        ],
        n=5,
        temperature=1.2,
    )

    outlines = [choice.message.content for choice in outlines_completion.choices]

    # Initialize messages with the ranking request
    messages = [
        {"role": "system", "content": "You are a helpful assistant, who's job is ranking outlines for children's books."},
        {"role": "user", "content": "Rank the following children's story outlines from 1 to 5, with 1 being the best and 5 being the least preferred:"}
    ]

    # Iterate through outlines and ask GPT to rank each one
    for outline in outlines:
        messages.append({"role": "user", "content": outline})

    messages.append({"role": "user", "content": "Now, provide the rankings.  Remember to simply rank them in order, do not explain your reasoning.  Include the outline titles in your rankings."})
    rankings = generate_response(messages, temperature=0.2, max_tokens=1000)
    
    best, title = match_best_outline(rankings, outlines)
    best = enhance_outline(best)
    
    return best, title



def build_first_draft(outline):
    model_engine = "gpt-3.5-turbo"

    # Initialize the list to store the generated sections
    sections = []


    # Split the outline into separate sections
    section_pattern = r'(?<=\n\n)[\s\S]*?(?=\n\n)'
    section_prompts = re.findall(section_pattern, outline)

    # Initialize the messages with the assistant's role
    messages = [
        {"role": "system", "content": "You are a helpful assistant who writes children's book sections based on provided outlines."},
        {"role": "user", "content": "You are an extremely talented and creative children's book author.  Together, we are going to write a children's book, step by step."}
    ]

    # Iterate through the section prompts and generate content for each section
    for prompt in section_prompts[1:]:
        
        messages.append({"role": "user", "content": f"Write a section for a children's book based on this part of the outline: '{prompt}'"})
        section_content = generate_response(messages, max_tokens=2000)
        messages.append({"role": "assistant", "content": section_content})
        sections.append(section_content)

    return sections



def continuity_check_prompt(prev_section, curr_section):
    return f"Does the following section maintain continuity and flow well with the previous section? Respond with only a single word, true or false.  Previous section: '{prev_section}'. Current section: '{curr_section}'"

def refine_draft(book_sections, title):
    refined_sections = [book_sections[0]]  # Add the first section as it doesn't need to be checked for continuity
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "system", "content": "You are an extremely talented editor of children's books.  Your specialty is ensuring that the story maintains cohesion, continuity and flows well together.  We're going to ensure that this children's story maintains continuity, step by step."}
    ]

    for i in range(1, len(book_sections)):
        prev_section = book_sections[i - 1]
        curr_section = book_sections[i]

        # Check if the current section maintains continuity with the previous section
        messages.append({"role": "user", "content": continuity_check_prompt(prev_section, curr_section)})
        response = generate_response(messages, temperature=0.2, max_tokens=10)

        while response.lower() not in ('true', 'false', 'true.', 'false.'):
            messages.append({"role": "user", "content": "Please respond with 'true' or 'false'."})
            response = generate_response(messages, temperature=0.2, max_tokens=10)
            print(response)

        # If the response is false, ask GPT to fix the section for better continuity and flow
        if response.lower() == 'false':
            messages.append({"role": "user", "content": f"Please fix this section so that it maintains continuity and flows well with the previous section. Current section: '{curr_section}'"})
            fixed_section = generate_response(messages, temperature=0.2, max_tokens=2000)
            refined_sections.append(fixed_section)
            messages.append({"role": "assistant", "content": fixed_section})
        else:
            refined_sections.append(curr_section)
            messages.append({"role": "assistant", "content": response})

    # Check for continuity between the first and last sections
    first_section = refined_sections[0]
    last_section = refined_sections[-1]

    messages.append({"role": "user", "content": continuity_check_prompt(first_section, last_section)})
    response = generate_response(messages, temperature=0.2, max_tokens=10)

    while response.lower() not in ('true', 'false', 'true.', 'false.'):
        messages.append({"role": "user", "content": "Please respond with only 'true' or 'false'."})
        response = generate_response(messages, temperature=0.2, max_tokens=10)

    if response.lower() == 'false':
        return "Got lost"
    else:
        return "\n\n".join([title,] + refined_sections)


