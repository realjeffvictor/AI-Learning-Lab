## Where names live

A variable created inside a function is **local**: it exists only while the function runs, and nothing outside can see it.

```python
def make_total():
    total = 10
    return total

make_total()
print(total)    # NameError: name 'total' is not defined
```

This is a feature. Functions can use any names they like without clashing with the rest of the program.

## Assigning does not reach outside

A function can **read** a name defined outside it, but assigning to a name inside creates a new local one:

```python
x = 5

def change():
    x = 10
    return x

print(change())   # 10
print(x)          # 5, the outside x was untouched
```

The reliable habit is to pass values **in** as parameters and send results **out** with `return`, instead of reaching for outside names.

## Lists are shared

There is one catch. A list passed to a function is not copied, so changes made to it inside the function are visible outside:

```python
def add_item(items):
    items.append("new")

basket = ["apple"]
add_item(basket)
print(basket)    # ['apple', 'new']
```

This is the same "two names, one list" behaviour you met in the lists lesson. If you want to leave the original alone, work on a copy: `items = items.copy()`.

## Small functions, one job each

A function that does one thing is easy to name, easy to test and easy to reuse. Compare:

```python
def clean_name(raw):
    return raw.strip().title()

def make_greeting(raw):
    return f"Hello, {clean_name(raw)}!"

print(make_greeting("  ada LOVELACE "))   # Hello, Ada Lovelace!
```

Functions can call other functions. If you struggle to name a function, it is probably doing too much.

## Checking with assert

An `assert` line checks that something is true and raises an `AssertionError` if it is not. It is the smallest possible test:

```python
def is_even(n):
    return n % 2 == 0

assert is_even(4)
assert not is_even(7)
assert is_even(0)
print("all good")
```

If any check failed, Python would stop with an `AssertionError` at that line. Writing a few asserts before you trust a function is a habit worth building now.

## Using AI for tests, carefully

An assistant is good at proposing test cases quickly. It is not good at knowing whether the **expected answers** are right, because it may calculate them with the same mistake as the code. Read every expected value and work out at least a few by hand. That is **Verify** applied to the tests themselves.

## Check yourself

After `x = 5` and a function whose body is `x = 10`, called once, what does `print(x)` show? And what error does a failing `assert 1 == 2` raise?

The answers are `5` and `AssertionError`.
