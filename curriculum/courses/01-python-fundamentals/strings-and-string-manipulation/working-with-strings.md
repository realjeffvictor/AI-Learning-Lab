## Text is a sequence of characters

A **string** is an ordered sequence of characters. Each character has a position called its **index**, and counting starts at 0.

```python
word = "Python"
print(word[0])     # P
print(word[5])     # n
print(word[-1])    # n, negative numbers count from the end
print(word[-2])    # o
print(len(word))   # 6
```

The characters of `"Python"` sit at positions 0 to 5: P, y, t, h, o, n.

Asking for a position that does not exist is an error: `word[10]` raises `IndexError: string index out of range`.

## Slicing

`text[start:stop]` takes the characters from `start` up to, but **not including**, `stop`.

```python
print(word[0:2])    # Py
print(word[2:])     # thon, from index 2 to the end
print(word[:3])     # Pyt, from the start up to index 3
print(word[::2])    # Pto, every second character
print(word[::-1])   # nohtyP, reversed
```

Unlike a single index, a slice is forgiving: `word[2:100]` simply gives `"thon"`.

## Joining and repeating

```python
print("Hello, " + "world")   # Hello, world
print("ha" * 3)              # hahaha
print("Age: " + str(36))     # Age: 36
```

`+` joins text with text only. `"Age: " + 36` fails with a `TypeError`, so convert the number first with `str()`. To go the other way, `int("5")` turns the text `"5"` into the number 5.

## Strings cannot be changed

```python
word = "Python"
word[0] = "J"      # TypeError: 'str' object does not support item assignment
```

You build a **new** string instead:

```python
print("J" + word[1:])   # Jython
```

## Quotes and special characters

```python
print("It's fine")        # It's fine
print("Line 1\nLine 2")   # two lines: \n means "new line"
print("Tab\there")        # \t means "tab"
```

Use single or double quotes, whichever avoids a clash with the text. Use `\` before a quote or letter for special characters.

## Verify slices

Off-by-one mistakes are the most common string bug, and AI tools make them too. When an assistant writes a slice such as "the last three characters", test it on a normal word and on a short one. `"Python"[-3:]` gives `hon`, and `"ab"[-3:]` quietly gives `ab` rather than an error. Decide whether that is what you want.

## Check yourself

What do these print?

1. `print("banana"[1::2])`
2. `print("banana"[::-1])`

The answers are `aaa` and `ananab`.
