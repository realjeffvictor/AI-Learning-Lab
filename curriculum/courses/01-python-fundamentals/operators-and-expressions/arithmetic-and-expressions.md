## Python is a calculator with a memory

An **expression** is a piece of code that Python can work out to a single value. `2 + 3` is an expression, and so is `price * quantity`. Programs are built from expressions, so it pays to know exactly how Python evaluates them.

## The arithmetic operators

```python
print(7 + 3)    # 10    addition
print(7 - 3)    # 4     subtraction
print(7 * 3)    # 21    multiplication
print(7 / 2)    # 3.5   division
print(7 // 2)   # 3     floor division
print(7 % 2)    # 1     remainder (modulo)
print(2 ** 10)  # 1024  power
```

Two of these surprise beginners:

- `/` always gives a float, even when the answer is whole: `8 / 2` is `4.0`.
- `//` divides and rounds **down**, and `%` gives what is left over. Together they split a number: `17 // 5` is `3` and `17 % 5` is `2`, because 17 = 3 x 5 + 2.

A worked example, turning 135 minutes into hours and minutes:

```python
total_minutes = 135
hours = total_minutes // 60
minutes = total_minutes % 60
print(hours, minutes)
```

This prints `2 15`.

## Order of evaluation

Python follows the order you know from maths: powers first, then multiplication, division, `//` and `%`, then addition and subtraction. Operators of the same rank go left to right, except `**`, which goes right to left.

```python
print(2 + 3 * 4)    # 14
print((2 + 3) * 4)  # 20
print(10 - 4 - 3)   # 3
print(2 ** 3 ** 2)  # 512, because it is 2 ** (3 ** 2)
```

When you are unsure, add parentheses. They cost nothing and make your intent obvious to the next reader.

## Floats are approximate

```python
print(0.1 + 0.2)              # 0.30000000000000004
print(round(0.1 + 0.2, 2))    # 0.3
```

Computers store decimal fractions in binary, so tiny errors appear. This is normal in every language. Round when you display a result, and never rely on an exact float answer.

## Verify what AI gives you

Suppose an assistant writes the average of two scores as `a + b / 2`. It looks fine, but precedence makes it `a + (b / 2)`. With `a = 4` and `b = 8` it returns `8.0`, not `6.0`.

The habit that catches this is **Verify**: test generated maths with numbers where you already know the answer. The habit that prevents it is **Direct**: when you ask for a formula, state it in words and give one example with the expected result.

## Check yourself

Work these out before running them:

1. `print(17 // 5, 17 % 5)`
2. `print(2 + 3 * 2 ** 2)`

The answers are `3 2` and `14`.
