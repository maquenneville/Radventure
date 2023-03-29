# Radventure - Children's Book Builder

Radventure is a powerful tool that helps you create engaging and cohesive children's books using OpenAI's GPT-3.5-turbo model. This Python application streamlines the process of generating prompts, outlines, and content for your children's book.

# Features
Customizable input for genre, target audience, theme, and additional details.
Enhanced prompts and outlines using GPT-3.5-turbo.
Automated drafting, editing, and continuity checks.
Export your final story as a text file.


# Dependencies
Python 3.6 or later
OpenAI Python package
Transformers Python package


# Usage
Install the required Python packages:

pip install openai transformers

Clone the repository or copy the BookBuilderHelpers.py and main script to your local machine.

Set up your OpenAI API key in a config.ini file. Refer to the instructions below.

Run the main script in your terminal:

python your_main_script_name.py

Follow the prompts to input your story's genre, target audience, theme, and additional details.

The script will create an enhanced prompt, outline, draft, and refine the story. Your final story will be saved as a .txt file in the same directory.

# API Key Setup
To use Radventure, you need to set up your OpenAI API key. Create a config.ini file in the same directory as your main script and BookBuilderHelpers.py with the following content:

[OpenAI]
api_key = your_openai_api_key_here

# Notes

Occasionally, the story produced will have some continuity issues (referring to characters that were never mentioned before, changing random details and characteristics partway through, etc).  Updates to prompt engineering in the script will continue to make this less likely, and access to gpt-4 will likely enhance the entire finished product.
