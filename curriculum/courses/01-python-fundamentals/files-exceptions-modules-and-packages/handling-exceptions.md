## Errors are objects you can catch

When something goes wrong, Python **raises an exception** and the program stops with a traceback. You have met many: `ValueError`, `TypeError`, `IndexError`, `KeyError`, `ZeroDivisionError`, `FileNotFoundError`. A `try` / `except` block lets your program deal with the problem and carry on.

```python
try:
    number = int("abc")
    print("converted")
except ValueError:
    print("not a number")
print("done")
```

This prints `not a number` and then `done`. The line `print("converted")` never ran, because the error happened on the line before it, and Python jumped straight to the `except`.

## Catch what you expect

Name the exceptions you expect. A bare `except:` that catches everything hides real bugs, including typing mistakes in your own code.

```python
def safe_divide(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        return None

print(safe_divide(10, 4))    # 2.5
print(safe_divide(1, 0))     # None
```

You can handle several kinds, in one `except` or several:

```python
try:
    value = int(text)
except (ValueError, TypeError):
    value = 0
```

## else and finally

```python
try:
    f = open("data.txt")
except FileNotFoundError:
    print("no data yet")
else:
    print("opened fine")
    f.close()
finally:
    print("always runs")
```

`else` runs only if nothing was raised. `finally` runs **no matter what**, which makes it the place for clean-up. In practice `with` handles most clean-up for you.

## Seeing the error itself

```python
try:
    {}["x"]
except KeyError as error:
    print("missing key:", error)
```

This prints `missing key: 'x'`. The name after `as` holds the exception object.

## Raising your own

Your own functions can refuse bad input by raising an exception:

```python
def set_age(age):
    if age < 0:
        raise ValueError("age cannot be negative")
    return age
```

Calling `set_age(-1)` stops with `ValueError: age cannot be negative`. Raising early with a clear message is much kinder to whoever debugs it than letting a strange error appear ten lines later.

## Do not silence errors

```python
try:
    risky()
except Exception:
    pass          # the error is swallowed and nobody ever knows
```

This is almost always a mistake. Either handle the error properly, or let it happen so you can see and fix it. Generated code is full of `except Exception: pass`, and it hides the very bugs you need to find. When you review it, **Verify** what happens on the failing path: does it tell the user something, or fail quietly?

## Check yourself

In `try: x = int("7") / 0 ... except ValueError: ... except ZeroDivisionError: print("zero")`, what is printed? And what does `finally` do?

The answers are `zero` (the `int("7")` works, the division fails), and `finally` runs whether or not an error occurred.
