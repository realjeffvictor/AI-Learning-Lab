## Code that lives in other files

Python ships with a large **standard library**: ready-made code organised into **modules**. You bring a module into your program with `import`.

```python
import math

print(math.sqrt(144))    # 12.0
print(math.pi)           # 3.141592653589793
print(math.floor(3.7))   # 3
```

You reach things inside a module with a dot. You can also import just what you need, or give a module a shorter name:

```python
from math import sqrt
import statistics as stats

print(sqrt(81))                   # 9.0
print(stats.mean([2, 4, 6]))      # 4
```

## Useful standard modules

- `math`: square roots, rounding, constants.
- `random`: random numbers and choices.
- `datetime`: dates and times.
- `json`: converting data to and from text.
- `os` and `pathlib`: working with files and folders.
- `collections`: extra container types such as `Counter`.

## JSON: the language of APIs

JSON is a text format for lists, dictionaries, numbers and strings. It is how most web services send data, so you will use it constantly from Stage 3 onward.

```python
import json

data = {"name": "Ada", "scores": [90, 85]}
text = json.dumps(data)
print(text)                      # {"name": "Ada", "scores": [90, 85]}
back = json.loads(text)
print(back["scores"][0])         # 90
print(type(text).__name__)       # str
```

`dumps` turns data **into** a string, and `loads` turns a string **back** into data. Together with the files lesson, this is how you save a dictionary and read it later.

## Your own modules

Any file ending in `.py` is a module. If `helpers.py` sits next to your program and contains a function `clean_name`, you can write:

```python
from helpers import clean_name
```

A common pattern at the bottom of a file lets it work both ways:

```python
if __name__ == "__main__":
    print("running directly")
```

The block runs when you start the file yourself, and is skipped when another file imports it.

## Packages

A **package** is a folder of modules, marked by a file called `__init__.py`. If a folder `tools` holds `__init__.py` and `text.py`, then `from tools.text import clean_name` works.

## Third-party packages

Millions of extra packages are published by other people. You install them with `pip`, ideally inside a **virtual environment** (the `.venv` folder in this project) so each project keeps its own set:

```text
pip install requests
```

On this platform's playground only the standard library is available, but you will use `requests`, `pandas` and others in later stages on your own machine.

## Be careful what you install

AI assistants sometimes invent package names, and attackers publish malicious packages with names that look plausible. Before you install anything an assistant suggests, **Verify** it: does the package exist on the official index, who maintains it, is it widely used, and is the name spelled exactly right? Installing unchecked code gives it full access to your computer. That is the **Own** principle applied to your dependencies.

## Check yourself

What is `json.loads('[1, 2]')`? And what does `if __name__ == "__main__":` protect against?

The answers are the list `[1, 2]`, and running that block when the file is only imported by another file.
