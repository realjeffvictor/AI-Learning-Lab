## Questions that have yes or no answers

A **comparison** asks a question about two values and answers with a boolean: `True` or `False`.

```python
print(5 > 3)    # True
print(5 < 3)    # False
print(5 >= 5)   # True
print(5 <= 4)   # False
print(5 == 5)   # True
print(5 != 5)   # False
```

Do not mix up the two equals signs. A single `=` **assigns** a value to a name. A double `==` **compares** two values.

## Combining answers: and, or, not

```python
age = 20
print(age >= 18 and age < 65)   # True, both parts are true
print(age < 18 or age >= 65)    # False, neither part is true
print(not age >= 18)            # False
```

`and` needs both sides true. `or` needs at least one. `not` flips the answer. Python also lets you chain comparisons the way maths does:

```python
print(18 <= age < 65)   # True
```

## Which runs first?

`not` goes first, then `and`, then `or`. That changes results:

```python
print(True or False and False)    # True, because `False and False` is worked out first
print((True or False) and False)  # False
```

Use parentheses whenever a condition mixes `and` with `or`.

## Comparing text and mixed types

```python
print("apple" == "apple")   # True
print("Apple" == "apple")   # False, capitals matter
print("apple" < "banana")   # True, compared letter by letter
print(5 == "5")             # False, a number is never equal to text
```

Using `<` between a number and text is an error: `5 < "5"` raises `TypeError: '<' not supported between instances of 'int' and 'str'`.

## Never compare floats with ==

```python
print(0.1 + 0.2 == 0.3)                    # False
print(abs((0.1 + 0.2) - 0.3) < 1e-9)       # True
```

Because floats are approximate, ask whether two numbers are *close enough* instead of *identical*.

## Working with AI

When you ask an assistant for a rule such as "a comfortable day is warm but not humid", the words are vague. **Direct** it with the exact limits: "temperature from 18 to 26 inclusive, and humidity below 60". Then **Verify** it with values on each side of every limit: 17, 18, 26 and 27.

## Check yourself

With `x = 7`, what do these print?

1. `print(x > 3 and x % 2 == 0)`
2. `print(not (x > 10) or x == 0)`

The answers are `False` and `True`.
