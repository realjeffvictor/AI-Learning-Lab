## A name attached to a value

A **variable** is a name attached to a value, so you can use the value later.

```python
price = 20
quantity = 3
total = price * quantity
print(total)
```

This prints `60`. The `=` sign here does not mean "equals" as in maths. It means "attach the name on the left to the value on the right".

## Reassignment

A name can be attached to a new value. The old value is forgotten.

```python
count = 1
count = count + 1
print(count)
```

Python works out the right side first (`1 + 1`), then attaches `count` to the result. This prints `2`. Programs change state this way, one assignment at a time.

## Four basic types

Every value has a **type**. The first four to learn:

```python
age = 30            # int: a whole number
height = 1.75       # float: a number with a decimal part
name = "Ada"        # str: text
is_student = True   # bool: True or False
print(type(age))
```

The last line prints `<class 'int'>`. The function `type()` is a quick way to check what you are holding.

## Naming rules

- Use letters, digits and underscores, and do not start with a digit.
- Names are case sensitive: `Total` and `total` are different.
- By convention, Python names use lowercase words joined by underscores, like `monthly_total`.

Choose names that say what the value means. `price` is better than `p`.

## Types matter

```python
print("5" + 3)
```

This fails with `TypeError: can only concatenate str (not "int") to str`. `"5"` is text and `3` is a number, and Python will not guess which kind of addition you meant.

## Check yourself

What does this print, and what is the type of `result`?

```python
result = "7" * 2
print(result)
```

Decide first, then work it out. Repeating text is allowed, so it prints `77`, and `result` is a `str`. If your answer was `14`, look again at the quotation marks around the 7.
