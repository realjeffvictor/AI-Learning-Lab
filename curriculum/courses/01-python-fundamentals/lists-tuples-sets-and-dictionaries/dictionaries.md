## Looking things up by name

A **dictionary** stores **key: value** pairs. You ask for a value by its key, not by a position.

```python
person = {"name": "Ada", "age": 36}
print(person["name"])    # Ada
print(len(person))       # 2
print("age" in person)   # True, `in` checks the keys
```

## Adding, updating and removing

```python
person["city"] = "London"    # adds a new key
person["age"] = 37           # updates an existing key
print(person)                # {'name': 'Ada', 'age': 37, 'city': 'London'}
del person["city"]           # removes it
print(person)                # {'name': 'Ada', 'age': 37}
```

Dictionaries remember the order in which keys were added.

## Missing keys

Asking for a key that is not there is an error:

```python
print(person["email"])   # KeyError: 'email'
```

The method `.get()` is the safe way. It returns `None`, or a default you choose:

```python
print(person.get("email"))             # None
print(person.get("email", "unknown"))  # unknown
```

## Keys, values and items

```python
print(list(person.keys()))     # ['name', 'age']
print(list(person.values()))   # ['Ada', 37]
print(list(person.items()))    # [('name', 'Ada'), ('age', 37)]
print(sum({"a": 1, "b": 2}.values()))   # 3
```

Loops, coming in a later module, will let you walk through a dictionary one item at a time.

## Rules for keys

A key must be something that cannot change: text, numbers and tuples work. A list cannot be a key. `{[1, 2]: "a"}` raises `TypeError: unhashable type: 'list'`. Values can be anything, including lists and other dictionaries:

```python
students = {"ada": {"age": 36, "scores": [90, 85]}}
print(students["ada"]["scores"][0])    # 90
```

## A counting pattern

```python
counts = {}
counts["a"] = counts.get("a", 0) + 1
counts["a"] = counts.get("a", 0) + 1
print(counts)     # {'a': 2}
```

`.get(key, 0)` supplies a starting value, so the first time a key appears it counts from zero.

## Reading API data

Almost every API you will meet in Stage 3 returns dictionaries inside dictionaries. Practise reading one now: say out loud what `data["user"]["name"]` means before you run it. When an AI writes code that digs into nested data, **Verify** it with `.get()` in mind: what happens if a key is missing?

## Check yourself

With `d = {"x": 1}`, what do these print?

1. `d["y"] = 5` then `print(len(d))`
2. `print(d.get("z", 0))`

The answers are `2` and `0`.
