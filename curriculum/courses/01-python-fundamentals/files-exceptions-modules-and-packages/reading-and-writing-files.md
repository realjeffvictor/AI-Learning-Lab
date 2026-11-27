## Making data last

Variables vanish when a program ends. A **file** keeps data on disk so the next run can use it. This is how the expense tracker project will save your expenses.

## Writing a file

```python
with open("notes.txt", "w") as f:
    f.write("first line\n")
    f.write("second line\n")
```

- `open(name, mode)` opens a file. The mode `"w"` means **write**, and it **erases** any existing content.
- `with ... as f:` closes the file for you when the block ends, even if something goes wrong. Always use it.
- `write` does not add a new line. You supply `\n` yourself.

## Modes

- `"r"`: read (the default). The file must already exist.
- `"w"`: write. Creates the file, or empties it if it exists.
- `"a"`: append. Adds to the end and keeps what is there.

Using `"w"` on a file you meant to add to is a classic way to lose data.

## Reading a file

```python
with open("notes.txt") as f:
    text = f.read()
print(text)
```

`read()` returns the whole file as one string. To go line by line, loop over the file:

```python
with open("notes.txt") as f:
    for line in f:
        print(line.strip())
```

Each line still ends with `\n`, which is why `.strip()` is used. Without it, `print` would show a blank line after each one. You can also call `f.readlines()` to get a list of lines.

## Files that are not there

```python
open("missing.txt")    # FileNotFoundError: [Errno 2] No such file or directory: 'missing.txt'
```

The next lesson shows how to handle that error instead of crashing.

## Where is the file?

A name like `"notes.txt"` is relative to the folder the program runs from. If you cannot find a file you wrote, print the folder:

```python
import os
print(os.getcwd())
```

## Text only

Files hold text. To save numbers or lists, convert them to text first, which is what the JSON format in the modules lesson is for. For now, `str(42)` makes `"42"` and `int("42")` brings it back.

## Where this runs here

On this platform your code runs inside your browser, with its own small private file system. Files you write in an exercise live only inside that sandbox and never touch your computer. On your own machine the same code writes real files.

## Safe habits with AI

Generated file code is where small mistakes become lost data. Check three things: the **mode** (`"w"` or `"a"`?), that it uses `with`, and what happens when the file does not exist yet. Ask for a tiny test with a throwaway file name, never your real data.

## Check yourself

What is the difference between `"w"` and `"a"`? And why does `print(line)` inside a file loop show blank lines between the lines?

The answers: `"w"` erases the file first, `"a"` adds to the end; each line ends with `\n`, so printing it adds a second newline.
