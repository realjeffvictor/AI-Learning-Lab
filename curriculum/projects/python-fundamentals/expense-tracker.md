## The goal

Build a small program you could actually use: a **personal expense tracker** that runs in the terminal.

It should let you record what you spend, remember it between runs, and tell you where your money goes.

## What it must do

Work through the checklist on the right. In short:

1. Add an expense (amount, category, note).
2. List expenses and show the total for each category.
3. Save to a file when you quit and load it when you start.
4. Survive bad input. Typing `abc` as an amount should produce a helpful message, not a crash.

## Suggested approach

- Represent one expense as a dictionary, and the whole list as a list of dictionaries.
- Write one small function per job: `add_expense`, `total_by_category`, `save`, `load`.
- Store the data as JSON text in a file. Python's standard `json` module does the conversion.
- Build it in small steps and run it after each one.

Some of the lessons this project draws on (files, exceptions, dictionaries) are still marked Planned on this platform. Use the AI assistant and the linked resources on the Progress page to fill the gaps, and apply the five principles while you do:

- **Direct:** when you ask an AI for help, say what you are building, what you have tried and what the error says.
- **Verify:** run every piece of generated code with normal input, empty input and bad input before you keep it.
- **Own:** you must be able to explain every line in your final program without looking at the AI's answer.

## What to submit

- **GitHub repository link.** Push your code to a public repository.
- **Documentation.** Paste your README here. It should say what the program does, how to run it, and show one example session.
- **Reflection.** Describe how you used AI (or chose not to), what you verified yourself, and what you would change next time.

A reviewer will open your repository, read your documentation and score your work against the rubric.
