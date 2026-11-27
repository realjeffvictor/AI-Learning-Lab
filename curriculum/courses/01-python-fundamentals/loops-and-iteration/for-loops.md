## Doing something many times

A **loop** repeats a block of code. The `for` loop repeats it once for each item in a collection.

```python
colors = ["red", "green", "blue"]
for color in colors:
    print(color)
```

This prints `red`, `green` and `blue`, one per line. On each pass, the name `color` is attached to the next item, and the indented block runs. The colon and indentation rules are the same as for `if`.

## Looping a set number of times: range

`range()` produces a sequence of numbers.

```python
for n in range(3):
    print(n)          # 0 then 1 then 2
for n in range(1, 4):
    print(n)          # 1 then 2 then 3
for n in range(0, 10, 3):
    print(n)          # 0 then 3 then 6 then 9
```

`range(stop)` starts at 0 and stops **before** `stop`. `range(start, stop)` starts where you say. `range(start, stop, step)` skips by `step`. As with slices, the stop value is never included, which is a favourite source of off-by-one mistakes.

## The accumulator pattern

Most loops build up a result. Start with a value before the loop, and update it on every pass:

```python
total = 0
for n in [3, 4, 5]:
    total += n
print(total)    # 12
```

`total += n` is shorthand for `total = total + n`. Building a list works the same way:

```python
squares = []
for n in range(1, 5):
    squares.append(n * n)
print(squares)   # [1, 4, 9, 16]
```

## Loops with decisions

Put an `if` inside a loop to count or filter:

```python
evens = 0
for n in range(1, 11):
    if n % 2 == 0:
        evens += 1
print(evens)    # 5
```

## Other things you can loop over

```python
for ch in "hi":
    print(ch)                    # h then i

prices = {"tea": 3, "milk": 2}
for name, price in prices.items():
    print(name, price)           # tea 3 then milk 2

for index, color in enumerate(["red", "green"]):
    print(index, color)          # 0 red then 1 green
```

Looping straight over a dictionary gives its **keys**. `.items()` gives key and value together, and `enumerate()` gives a counter along with each item.

## Two traps

- After the loop, the loop variable keeps the **last** value it had.
- Do not add or remove items from a list while you loop over it. The loop gets confused. Build a new list instead.

## Tracing a loop by hand

When a loop surprises you, write a small table: one row per pass, with the value of each variable. That is the same habit that lets you check loops written by an AI. Ask yourself what the code does on the **first** pass, the **last** pass, and with an **empty** collection, where the body should run zero times.

## Check yourself

What does `for i in range(3): print(i * 2)` print? And what is `len(range(2, 10, 3))`?

The answers are `0`, `2`, `4` on separate lines, and `3`, because the values are 2, 5 and 8.
