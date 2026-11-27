## Building on an existing class

**Inheritance** lets a new class start from an existing one and change only what differs. The new class is the **subclass**, and the one it builds on is the **base class**.

```python
class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        return "..."

class Dog(Animal):
    def speak(self):
        return "Woof"

class Cat(Animal):
    def speak(self):
        return "Meow"

d = Dog("Rex")
print(d.name)       # Rex
print(d.speak())    # Woof
print(Animal("Generic").speak())    # ...
```

`Dog(Animal)` means "Dog is built on Animal". `Dog` gets `__init__` and `name` for free, and **overrides** `speak` with its own version.

## Extending __init__ with super()

When a subclass needs extra data, call the base class's `__init__` with `super()` and then add to it:

```python
class Puppy(Dog):
    def __init__(self, name, age):
        super().__init__(name)
        self.age = age

p = Puppy("Bit", 1)
print(p.name, p.age, p.speak())    # Bit 1 Woof
```

## Checking types

```python
print(isinstance(p, Puppy))     # True
print(isinstance(p, Animal))    # True, a Puppy is also a Dog and an Animal
print(isinstance(d, Cat))       # False
```

## Printing an object

By default, printing an object shows something unhelpful like `<__main__.Dog object at 0x7f...>`. Define the special method `__str__` and `print` will use it:

```python
class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        return "..."

    def __str__(self):
        return f"{self.name} says {self.speak()}"

class Dog(Animal):
    def speak(self):
        return "Woof"

print(Dog("Rex"))     # Rex says Woof
print(str(Dog("Rex")))
```

Notice that `__str__` is written once, in `Animal`, and still gives the right answer for a `Dog`, because it calls `self.speak()`, which finds the Dog version. That is the payoff of inheritance: shared code that adapts to each subclass.

## Prefer small hierarchies

Inheritance describes an **is-a** relationship: a Dog is an Animal. If the relationship is really **has-a** (a car has an engine), store the other object as an attribute instead:

```python
class Engine:
    def __init__(self, power):
        self.power = power

class Car:
    def __init__(self, engine):
        self.engine = engine
```

Deep chains of subclasses are hard to follow. If you find yourself three levels down, ask whether a simple attribute or function would do.

## Reviewing AI-designed hierarchies

An assistant asked to "design classes for a school" may invent a tall tree of subclasses. **Verify** the design against your real needs: which classes actually behave differently? Remove any that only exist to look tidy. Judging a design like this is part of **Own**.

## Check yourself

If `Cat` does not define `speak`, what does `Cat("Tom").speak()` return given the `Animal` above? And what does `isinstance(Dog("Rex"), Animal)` show?

The answers are `...` and `True`.
