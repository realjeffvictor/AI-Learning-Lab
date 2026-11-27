## A prompt is a small specification

Vague prompts get vague code. Compare:

> Make a login.

with:

> Write a Python function `check_password(password)` that returns `True` if the password has at least 10 characters and contains at least one digit, otherwise `False`. Use only the standard library. Example: `check_password("abcdefghi1")` returns `True`, and `check_password("short1")` returns `False`.

The second one says *what*, *for what*, *with what limits* and *how to tell if it worked*.

## Five parts of a good prompt

1. **Goal:** what you want, in one or two sentences.
2. **Context:** the language, the project, the data, what already exists.
3. **Constraints:** what the answer must or must not do, such as "standard library only" or "do not change the function signature".
4. **Example:** a sample input and the output you expect.
5. **Format:** how you want the answer, such as "code only" or "code, then a short explanation".

You will not need all five every time, but when an answer disappoints you, one of them is usually missing.

## Examples make the work checkable

An example input and expected output does two jobs. It tells the assistant what you mean, and it gives **you** a test you can run on the result. If you cannot write an example, you do not understand the problem yet. That is worth discovering *before* you generate any code.

## Ask for a plan first

For anything bigger than a small function, ask for a plan before code:

> Before writing any code, list the steps you would take and any questions you have.

Reading a five-line plan costs seconds and can catch a wrong approach before it becomes two hundred lines you would have to unpick. You can also invite questions: "Ask me anything that is unclear before you start."

## Keep tasks small

One request, one job. "Write the function to parse the date" is better than "build the whole booking system". Small answers are easier to read, test and replace. Build the system from pieces that each passed your own check.

## When the answer is wrong

Do not just say "that is wrong". Give it something to work with:

> `average([])` crashes with ZeroDivisionError. I expected it to return 0. Here is the function and the full error message. What is the cause, and what is the smallest change that fixes it?

The input, the actual result, the expected result and the exact error are the most useful things you can supply. If the conversation gets confused, start a fresh one with a short summary of what you know.

## Be honest about your level

Saying "I am a beginner, please explain each step" changes the answer for the better. Saying "do not explain, I only want the code" changes it too. Tell it what helps you.

## Keep what works

When a prompt gives you a good result, save it. Over time you build a small library of prompts for the jobs you do often, and you improve them with each use.

## Never paste a secret into a prompt

Everything in these examples works with fake values. Replace real keys, passwords and personal data with placeholders first.

## Check yourself

Rewrite "make a function to clean names" as a prompt with a goal, context, a constraint and an example. Then ask: could I test the answer with my example?
