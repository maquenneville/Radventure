# -*- coding: utf-8 -*-
"""
Created on Tue Mar 28 21:37:46 2023

@author: marca
"""

import os
import threading
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from ttkthemes import ThemedTk
import tkinter.font as tkFont
from BookBuilderHelpers import *
import sys
import tkinter.scrolledtext as ScrolledText


class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None

    def show_tooltip(self):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25

        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")

        label = tk.Label(self.tooltip, text=self.text, background="lightyellow", relief="solid", borderwidth=1)
        label.pack()

    def hide_tooltip(self):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

def create_tooltip(widget, text):
    tooltip = ToolTip(widget, text)
    widget.bind("<Enter>", lambda event: tooltip.show_tooltip())
    widget.bind("<Leave>", lambda event: tooltip.hide_tooltip())
    return tooltip


def update_progress(msg):
    progress_messages.insert(tk.END, msg)
    progress_messages.see(tk.END)
    root.update_idletasks()
    
    
def create_story_thread():
    create_story_thread = threading.Thread(target=create_story)
    create_story_thread.start()


def create_story():
    genre = genre_entry.get()
    target_audience = target_audience_entry.get()
    theme = theme_entry.get()
    setting = setting_entry.get()
    content_hint = content_hint_entry.get("1.0", tk.END).strip()
    twisted = twist_var.get()

    try:
        update_progress("\nCreating a prompt based on your ideas...\n")

        prompt = build_prompt(
            genre, target_audience, theme, setting, content_hint, twist=twisted
        )
        enhanced = enhance_build_prompt(prompt)

        update_progress("Coming up with cool, different plot ideas, and picking the best one...\n")

        outline, title = select_best_outline(enhanced)

        update_progress("Writing your story...\n")

        sections = build_first_draft(outline)
        if len(sections) == 0:
            sections = build_first_draft(outline)

        update_progress("Trimming the story down to make it less repetitive...\n")

        concise = process_story_sections(sections)

        update_progress("Checking your story so it makes sense...\n")

        with concurrent.futures.ThreadPoolExecutor() as executor:
            photo_future = executor.submit(generate_photo_with_backoff, outline, title)
            refined_future = executor.submit(refine_draft_with_backoff, sections, title)

            description, photo_file = photo_future.result()
            refined_draft = refined_future.result()

        update_progress("Checking it one more time...\n")

        final_draft = edit_story_continuity(refined_draft)

        update_progress("Printing your story...\n")

        output_path = f"{output_folder.get()}/{title.replace(' ', '_')}_storybook.pdf"
        create_finished_copy(photo_file, title, final_draft, output_path)

        update_progress(f"Story '{title}' created and saved as '{output_path}'.\n")

    except Exception as e:
        update_progress(f"Error: {e}\n")





def select_output_folder():
    folder_path = filedialog.askdirectory()
    output_folder.set(folder_path)


root = tk.Tk()
root.title("Radventure")
root.geometry("700x600")

logo = tk.Label(root, text="Radventure!", font=("Helvetica", 24, "bold italic"), fg="red")
logo.grid(row=0, column=0, sticky="w", padx=10, pady=10)
logo_tooltip = create_tooltip(logo, "A build-your-own story tool, where anything is possible!")

input_width = 60

genre_label = tk.Label(root, text="Genre:")
genre_label.grid(row=1, column=0, sticky="e")
genre_entry = tk.Entry(root, width=input_width)
genre_entry.grid(row=1, column=1, sticky="w")
genre_tooltip = create_tooltip(genre_entry, "Input a genre, typically a single word (uplifting, affirming, relaxing, funny, etc.)")

target_audience_label = tk.Label(root, text="Target audience:")
target_audience_label.grid(row=2, column=0, sticky="e")
target_audience_entry = tk.Entry(root, width=input_width)
target_audience_entry.grid(row=2, column=1, sticky="w")
target_audience_tooltip = create_tooltip(target_audience_entry, "Input the target audience (5 year olds, 10 year olds, fifth graders, etc.)")

theme_label = tk.Label(root, text="Theme:")
theme_label.grid(row=3, column=0, sticky="e")
theme_entry = tk.Entry(root, width=input_width)
theme_entry.grid(row=3, column=1, sticky="w")
theme_tooltip = create_tooltip(theme_entry, "Input a theme (the value of friendship, eating your vegetables, the importance of labor power in society, etc.)")


setting_label = tk.Label(root, text="Setting:")
setting_label.grid(row=4, column=0, sticky="e")
setting_entry = tk.Entry(root, width=input_width)
setting_entry.grid(row=4, column=1, sticky="w")
setting_tooltip = create_tooltip(setting_entry, "Input the setting (a jungle, a coal mine, a dragon's lair, etc.)")


content_hint_label = tk.Label(root, text="Additional context:")
content_hint_label.grid(row=5, column=0, sticky="e")
content_hint_entry = tk.Text(root, height=3, width=input_width)
content_hint_entry.grid(row=5, column=1)
content_hint_tooltip = create_tooltip(content_hint_entry, "Input the any additional details you want for the story.")


twist_label = tk.Label(root, text="Twist:")
twist_label.grid(row=6, column=0, sticky="e")
twist_var = tk.BooleanVar()
twist_checkbutton = ttk.Checkbutton(root, variable=twist_var)
twist_checkbutton.grid(row=6, column=1, sticky="w")
twist_checkbutton_tooltip = create_tooltip(twist_checkbutton, "If selected, the story writer will try to incorporate a twist (may not always make a twist)")


progress_messages = tk.Text(root, height=10, width=70)
progress_messages.grid(row=7, column=0, columnspan=2, padx=10, pady=10)

output_folder = tk.StringVar()
output_folder_label = tk.Label(root, text="Output folder:")
output_folder_label.grid(row=8, column=0, sticky="e")
output_folder_entry = tk.Entry(root, textvariable=output_folder)
output_folder_entry.grid(row=8, column=1, sticky="w")
output_folder_button = tk.Button(root, text="Select", command=select_output_folder)
output_folder_button.grid(row=8, column=1)
output_folder_tooltip = create_tooltip(output_folder_entry, "Select the folder you want the story to be created in.")


create_button = tk.Button(root, text="Create Story", command=create_story_thread)
create_button.grid(row=9, column=1, pady=10, sticky='w')

root.mainloop()
