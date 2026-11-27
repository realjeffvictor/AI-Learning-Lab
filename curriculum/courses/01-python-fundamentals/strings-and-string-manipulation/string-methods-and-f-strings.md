## Methods: actions that belong to a value

A **method** is a function attached to a value and called with a dot. Strings come with many.

```python
print("  Hello, World  ".strip())   # Hello, World
print("hello".upper())              # HELLO
print("HELLO".lower())              # hello
print("ada lovelace".title())       # Ada Lovelace
print("a-b-c".replace("-", "+"))    # a+b+c
print("a,b,c".split(","))           # ['a', 'b', 'c']
print("-".join(["a", "b", "c"]))    # a-b-c
print("banana".find("an"))          # 1, the index where it starts
print("banana".find("x"))           # -1, which means "not found"
print("banana".count("a"))          # 3
print("Python".startswith("Py"))    # True
print("an" in "banana")             # True
```

## Methods return new strings

Because strings cannot be changed, a method never modifies the original. It returns a new string:

```python
s = "hi"
s.upper()
print(s)          # hi, unchanged
s = s.upper()
print(s)          # HI, now we kept the result
```

You can chain methods, each working on the result of the one before:

```python
print("  ada  ".strip().title())   # Ada
```

## f-strings: text with values inside

Put an `f` before the opening quote and write expressions inside `{}`:

```python
name = "Ada"
age = 36
print(f"{name} is {age}")            # Ada is 36
print(f"Next year: {age + 1}")       # Next year: 37
print(f"Price: {4.5:.2f}")           # Price: 4.50
print(f"Big: {1234567:,}")           # Big: 1,234,567
```

After the colon you can control formatting. `.2f` means "a float with two decimal places".

## Cleaning data with AI

Cleaning messy text is a good job to hand to an assistant, and a good place to practise **Direct** and **Verify**.

- **Direct:** give it one real example of the input and the exact output you want, not just a description.
- **Verify:** try the result on an empty string, extra spaces, and ALL CAPS. Tools often handle the example you showed and break on the next case.

## Check yourself

What does each print?

1. `print("a,b,c,d".split(",")[2])`
2. `print(f"{3.14159:.2f}")`

The answers are `c` and `3.14`.
