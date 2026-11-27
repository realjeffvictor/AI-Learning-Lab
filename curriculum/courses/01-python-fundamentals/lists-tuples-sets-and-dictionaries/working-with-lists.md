## An ordered, changeable collection

A **list** holds several values in order. Create one with square brackets. Indexing and slicing work exactly as they do for strings.

```python
fruits = ["apple", "banana", "cherry"]
print(fruits[0])      # apple
print(fruits[-1])     # cherry
print(fruits[1:])     # ['banana', 'cherry']
print(len(fruits))    # 3
print("banana" in fruits)   # True
```

A list may hold values of different types, and it can be empty: `[]`.

## Changing a list

Unlike a string, a list can be changed in place:

```python
numbers = [3, 1, 2]
numbers.append(4)        # [3, 1, 2, 4]
numbers.insert(0, 10)    # [10, 3, 1, 2, 4]
last = numbers.pop()     # removes 4 and gives it back, so last is 4
numbers.remove(3)        # removes the first 3
print(numbers)           # [10, 1, 2]
numbers[0] = 99
print(numbers)           # [99, 1, 2]
```

Using an index that does not exist raises `IndexError: list index out of range`.

## Totals and sorting

```python
scores = [70, 95, 82]
print(sum(scores))             # 247
print(min(scores), max(scores))  # 70 95
print(sorted(scores))          # [70, 82, 95]
print(sorted(scores, reverse=True))  # [95, 82, 70]
print(scores)                  # [70, 95, 82], sorted() did not change it
```

`sorted()` returns a **new** list. The method `scores.sort()` sorts the list itself and returns `None`, which causes a classic bug:

```python
x = [3, 1, 2].sort()
print(x)    # None
```

## Two names, one list

Assigning a list to another name does not copy it. Both names point at the same list:

```python
a = [1, 2]
b = a
b.append(3)
print(a)    # [1, 2, 3], a changed too
```

To make an independent copy, use `b = a.copy()` or `b = a[:]`.

## Joining and repeating

```python
print([1, 2] + [3])    # [1, 2, 3]
print([0] * 3)         # [0, 0, 0]
```

## Understand before you trust

AI-generated code often mutates a list that the rest of the program is still using, and the symptom shows up far from the cause. When code behaves strangely, ask: *did something change this list in place?* That question is the **Understand** principle at work.

## Check yourself

With `items = [5, 8, 1]`, what does each print, one after the other?

1. `items.append(7)` then `print(len(items))`
2. `print(sorted(items)[0])`

The answers are `4` and `1`.
