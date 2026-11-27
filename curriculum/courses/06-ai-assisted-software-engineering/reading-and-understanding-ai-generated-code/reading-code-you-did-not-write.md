## Code you did not write is code you must read

AI-generated code often arrives complete, tidy and confident. That makes it easy to accept without reading. This lesson gives you a routine for reading it properly. The same routine works on code from a teammate or from the internet.

## Step 1: say what it is supposed to do

Before reading a line, write one sentence: *what should this do, for which inputs, returning what?* If you cannot, go back and clarify the task.

## Step 2: read top to bottom, then trace an example

Read it once for the shape. Then pick a small input and **trace** it by hand: write down the value of each variable after each line. Tracing finds more bugs than staring does. Here is a typical generated function:

```python
def is_palindrome(text):
    return text == text[::-1]
```

It looks right. Trace `"Racecar"`: the reversed text is `"racecaR"`, which is not equal because of the capital letters, so it returns `False`. Whether that matters depends on what you wanted. The **assumption** (capitals count, spaces count) was hidden until you traced it.

## Step 3: list the assumptions and try to break them

Ask of every function:

- What if the input is empty?
- What if it has capitals, spaces or punctuation?
- What if it is very large, negative or zero?
- What if a value is missing?

An assistant usually shows you the example that works. The inputs that break it are your job.

## Step 4: check that everything it uses is real

Generated code may call a function that does not exist, use an option with the wrong name, or import a package nobody has published. A convincing name proves nothing.

- Run the code. A missing function fails immediately.
- For a package you do not know, check the official index, the maintainers and how widely it is used before installing. Attackers publish look-alike names.

## Step 5: look for security smells

These deserve a closer look every time:

- Secrets written into the code (keys, passwords).
- Building a database query by pasting user input into the text.
- `eval()` or running text as code.
- Turning off checks, such as certificate or permission checks, to make an error go away.
- Reading or writing files at paths the user controls.

The classic is SQL injection. This code builds a query by joining text:

```python
cursor.execute(f"SELECT * FROM users WHERE name = '{name}'")
```

If `name` is `x' OR '1'='1`, the query's meaning changes and returns every user. The fix is a **parameterized query**, which keeps the data separate from the command:

```python
cursor.execute("SELECT * FROM users WHERE name = ?", (name,))
```

Now whatever the user types is treated only as a value, never as part of the command.

## Step 6: is it more than you asked for?

Generated code often adds classes, options and layers you did not request. Extra code is extra surface for bugs and extra work to maintain. Remove what you do not need.

## Ask it to explain, then check the explanation

Asking the assistant to explain its own code line by line is useful for learning, but the explanation can contain mistakes too. Trust what you can confirm by running something.

## Check yourself

Why does "it worked on the example the assistant showed" prove very little? What are two inputs you would try on `is_palindrome` that the example may not have covered?
