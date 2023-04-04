# Radventure - Children's Book Builder

Radventure is a Python script that uses OpenAI's GPT-3.5-turbo to generate a unique story based on user input. The script takes user input for genre, target audience, theme, setting, content hint, and a twist option. It generates a story outline, writes a draft, refines the draft, and creates a finished PDF copy with a generated photo, title, and story text.

# Features
Customizable input for genre, target audience, theme, setting, additional details and an optional twist.
Enhanced prompts and outlines using GPT-3.5-turbo.
Automated drafting, editing, and continuity checks.
Automated cover photo generation.
Export your final story as a pdf file with an appropriate cover photo for the story.


# Dependencies
Python 3
OpenAI Python package
Requests
Pillow
ReportLab
Backoff
Transformers


# Usage
Install the required Python packages:

pip install openai backoff requests pillow reportlab transformers 

Clone the repository or copy the BookBuilderHelpers.py and BookBuilderTest.py to your local machine.

Set up your OpenAI API key in a config.ini file (refer to the instructions below).

Run the main script in your terminal:

python BookBuilderTest.py

Follow the prompts to input your story's genre, target audience, theme, setting, additional details and if you'd like a twist.

The script will create an enhanced prompt, outline, draft, edit, refine and create a photo for the story. Your final story will be saved as a .pdf file in the same directory.

4/4/2023 - You can now use the BookBuilderGUI.py file to run a simple tkinter-based GUI for Radventure

# API Key Setup
To use Radventure, you need to set up your OpenAI API key. Create a config.ini file in the same directory as your main script and BookBuilderHelpers.py with the following content:

[OpenAI]
api_key = your_openai_api_key_here

# Notes

Occasionally, the story produced will have some continuity issues (referring to characters that were never mentioned before, changing random details and characteristics partway through, etc).  Updates to prompt engineering in the script will continue to make this less likely, and access to gpt-4 will likely enhance the entire finished product.
