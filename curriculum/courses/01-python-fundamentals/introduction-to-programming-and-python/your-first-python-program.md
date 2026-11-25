## Display something

The smallest useful Python program is one line:

```python
print("Hello, world")
```

`print` is a **function**. The parentheses hold what you give it, and the quotation marks mark text, which Python calls a **string**. Running the line displays:

```text
Hello, world
```

## Lines run top to bottom

```python
# This line is a comment. Python ignores it.
print("Hello, world")
print("Python runs lines top to bottom")
```

A line starting with `#` is a **comment**: a note for humans. Python reads the other two lines in order, so the output has two lines, in that order.

## Text or arithmetic?

Predict what each line displays, then check the answers below.

```python
print("2 + 2")
print(2 + 2)
```

The first prints `2 + 2`, because it is text in quotation marks. The second prints `4`, because Python calculates it first.

## What mistakes look like

Python is strict, and its error messages are information. Two you will meet in the first week:

```python
print("Hello, world"
```

This raises `SyntaxError: '(' was never closed`. The parenthesis was opened and never closed.

```python
Print("Hello, world")
```

This raises `NameError: name 'Print' is not defined`. Python is case sensitive, so `Print` and `print` are different names.

## Working with an AI assistant

If an error confuses you, give the assistant the **whole** error message and the code that caused it. That is the **Direct** principle: more context gives a better answer. Then **Verify** the explanation by changing the code and watching whether the error behaves the way the assistant said it would.
