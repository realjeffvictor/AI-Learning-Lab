## Tuples: a list that cannot change

A **tuple** is an ordered collection written with parentheses. Once created, it cannot be changed.

```python
point = (3, 4)
print(point[0])      # 3
print(len(point))    # 2
point[0] = 5         # TypeError: 'tuple' object does not support item assignment
```

A tuple with one item needs a trailing comma: `(5,)`. Without it, `(5)` is just the number 5 in parentheses.

Tuples shine when a few values belong together, like a point or a name and an age. You can **unpack** one into separate names:

```python
x, y = point
print(x, y)     # 3 4

a, b = 1, 2
a, b = b, a     # swap two values
print(a, b)     # 2 1
```

## Sets: unique items with no order

A **set** holds each value at most once, and does not keep any order.

```python
numbers = set([1, 2, 2, 3, 3, 3])
print(len(numbers))        # 3
print(2 in numbers)        # True

colors = {"red", "green", "blue"}
colors.add("red")          # already there, nothing changes
colors.add("pink")
colors.remove("green")
print(len(colors))         # 3
```

Do not rely on the order a set prints in. It can differ between runs. When you need an ordered result, use `sorted()`:

```python
print(sorted(set([3, 1, 3, 2])))    # [1, 2, 3]
```

That one line removes duplicates from a list, which is the most common use of a set.

## Combining sets

```python
a = {1, 2, 3}
b = {3, 4}
print(a | b)    # {1, 2, 3, 4}  everything in either
print(a & b)    # {3}           only what is in both
print(a - b)    # {1, 2}        in a but not in b
```

## A trap with empty braces

`{}` is **not** an empty set. It is an empty dictionary, which comes in the next lesson. To make an empty set, write `set()`.

## Choosing between them

- **List:** ordered, changeable, duplicates allowed. The default choice.
- **Tuple:** ordered, fixed. Good for a small group of values that belong together.
- **Set:** unique values, no order, fast membership checks.

Choosing the right structure is a skill AI cannot do *for* you, because it depends on what your program needs. When an assistant picks a list where a set would do, you should be the one who notices.

## Check yourself

What does each print?

1. `print(len({1, 1, 2}))`
2. `a, b = (10, 20)` then `print(a + b)`

The answers are `2` and `30`.
