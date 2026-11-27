## Bundling data with the actions on it

So far you have kept data in variables and behaviour in functions. A **class** bundles the two: it is a blueprint for a kind of thing, describing what data it holds and what it can do. An **object** (also called an **instance**) is one thing built from that blueprint.

```python
class Account:
    def __init__(self, owner, balance=0):
        self.owner = owner
        self.balance = balance

    def deposit(self, amount):
        self.balance += amount

acct = Account("Ada", 100)
acct.deposit(50)
print(acct.owner, acct.balance)    # Ada 150
```

## The pieces

- `class Account:` starts the blueprint. Class names are written in CapitalisedWords by convention.
- `__init__` is a special method that runs automatically when you create an object. It sets up the object's starting data.
- `self` is the object itself. Every method receives it as its first parameter, and Python fills it in for you: you write `acct.deposit(50)`, not `acct.deposit(acct, 50)`.
- `self.balance` is an **attribute**: a piece of data stored on that particular object.
- A function defined inside a class is called a **method**.

## Many objects, separate data

```python
a = Account("Ada", 100)
b = Account("Linus")
a.deposit(25)
print(a.balance)    # 125
print(b.balance)    # 0
```

Each object keeps its own attributes. Changing `a` does not touch `b`.

## Methods that return answers

A method is just a function with access to `self`, so everything you know about `return` applies:

```python
class Account:
    def __init__(self, owner, balance=0):
        self.owner = owner
        self.balance = balance

    def withdraw(self, amount):
        if amount > self.balance:
            return False
        self.balance -= amount
        return True

acct = Account("Ada", 100)
print(acct.withdraw(30), acct.balance)     # True 70
print(acct.withdraw(500), acct.balance)    # False 70
```

The method protects the rule "you cannot withdraw more than you have". Putting a rule next to the data it protects is the main reason to use a class.

## A frequent mistake

Forgetting `self.` inside a method creates an ordinary local variable that disappears when the method ends:

```python
def deposit(self, amount):
    balance += amount        # UnboundLocalError
```

Inside a method, attributes are always reached through `self`.

## When a class is worth it

Use a class when you have several pieces of data that belong together **and** actions on them, such as a user, an order or a game piece. For a single value or a quick calculation, a variable or function is simpler. Beginners (and AI assistants) often reach for classes too early.

## Reading generated classes

AI tools produce classes quickly, often with more attributes and methods than you asked for. **Understand** each one before you keep it: what does `__init__` set, which methods change the state, and which only report it? Then **Verify** by creating two objects and checking that changing one leaves the other alone.

## Check yourself

After `a = Account("Ada", 100)` and `a.deposit(50)`, what is `a.balance`? And what does `self` refer to inside `deposit`?

The answers are `150` and the object the method was called on, here `a`.
