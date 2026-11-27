## Naming a piece of work

A **function** packages some code under a name so you can run it whenever you like. You have already called functions such as `print()` and `len()`. Now you will write your own.

```python
def greet(name):
    return f"Hello, {name}!"

print(greet("Ada"))    # Hello, Ada!
print(greet("Linus"))  # Hello, Linus!
```

The pieces:

- `def` starts the definition, followed by the function's name and parentheses.
- `name` is a **parameter**: a variable that receives the value you pass in.
- The indented block is the **body**.
- `return` hands a value back to whoever called the function.

Defining a function does not run it. Calling `greet("Ada")` does.

## return is not print

This is the most important distinction in the lesson.

```python
def add(a, b):
    return a + b

def show(a, b):
    print(a + b)

x = add(2, 3)
y = show(2, 3)    # this prints 5
print(x)          # 5
print(y)          # None
```

`return` gives a value **back** so you can use it. `print` only displays something. A function with no `return` gives back `None`, which is how many beginners end up with `None` in their results.

Once a `return` runs, the function ends immediately.

## Default values and keyword arguments

A parameter can have a default, used when the caller leaves it out:

```python
def power(base, exponent=2):
    return base ** exponent

print(power(5))                  # 25
print(power(2, 10))              # 1024
print(power(exponent=3, base=2)) # 8
```

In the last call the arguments are named, so their order no longer matters. Parameters with defaults must come after those without.

## Returning several values

A function can return several values separated by commas. They arrive as a tuple, which you can unpack:

```python
def min_max(numbers):
    return min(numbers), max(numbers)

low, high = min_max([4, 9, 2])
print(low, high)    # 2 9
```

## Docstrings

The first line of the body can be a string that explains the function:

```python
def average(numbers):
    """Return the mean of a list of numbers."""
    return sum(numbers) / len(numbers)
```

Good docstrings are short and say what goes in and what comes out.

## Testing a function

Call it with an ordinary input and with the awkward ones. What does `average([])` do? It divides by zero and raises `ZeroDivisionError`. You decide what the right behaviour is, perhaps returning 0, and write that into the function.

When you ask an AI for a function, **Direct** it with a name, the parameters, what it returns, and one example with the expected answer. Then **Verify** with the edge cases it did not mention.

## Check yourself

With `def add(a, b): return a + b`, what does `print(add(2, 3) * 2)` show? And with `def f(x): x * 2` (no return), what does `print(f(4))` show?

The answers are `10` and `None`.
