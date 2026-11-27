## Programs that choose

So far every line of your programs has run, in order. A **conditional statement** lets a program choose: run some lines only when a condition is true.

```python
temperature = 30
if temperature > 25:
    print("hot")
```

This prints `hot`. If `temperature` were 20, nothing would print, because the condition `temperature > 25` would be `False`.

Two details matter, and both cause beginner errors:

- The line ends with a **colon**.
- The lines that belong to the `if` are **indented** (use four spaces). The indentation is how Python knows which lines are inside the `if`. Forgetting it raises an `IndentationError`.

## else and elif

```python
temperature = 30
if temperature > 25:
    print("hot")
elif temperature > 15:
    print("mild")
else:
    print("cold")
```

Python checks the conditions from the top and runs **only the first branch that is true**, then skips the rest. Here it prints `hot`. With `temperature = 20` it prints `mild`, and with 5 it prints `cold`. `elif` means "else, if", and `else` has no condition because it catches everything left.

## Order matters

Because only the first true branch runs, the order of your checks changes the result:

```python
score = 95
if score >= 70:
    grade = "C"
elif score >= 90:
    grade = "A"
print(grade)    # C, which is wrong
```

95 is at least 70, so the first branch wins and the `A` branch is never reached. Check the **strictest** condition first: 90, then 80, then 70.

## Conditions that combine

Everything from the comparisons lesson works here:

```python
age = 20
has_ticket = True
if age >= 18 and has_ticket:
    print("welcome")
```

## Truthiness

Python lets any value stand in for a condition. These are treated as `False`: `0`, `0.0`, the empty string `""`, the empty list `[]`, the empty dictionary `{}` and `None`. Almost everything else is `True`.

```python
name = ""
if name:
    print("Hello", name)
else:
    print("No name given")
```

This prints `No name given`. You can check a value yourself with `bool()`: `bool("")` is `False`, `bool("a")` is `True`, and `bool([0])` is `True` because the list is not empty.

## A common slip

```python
if x = 5:      # SyntaxError: you meant ==
```

A single `=` assigns. Use `==` to compare.

## Testing branches with AI

An assistant will happily write a long `if/elif` chain. The bugs hide at the **boundaries**. When you check the code, **Verify** every branch with a value just below, exactly on, and just above each limit, for example 69, 70 and 71. If you ask an AI to write the chain, **Direct** it by saying whether each limit is inclusive: "90 and above is an A" leaves no doubt.

## Check yourself

With `score = 80` and the chain 90 is A, 80 is B, otherwise C, what is printed? And what does `print(bool(0))` show?

The answers are `B` and `False`.
