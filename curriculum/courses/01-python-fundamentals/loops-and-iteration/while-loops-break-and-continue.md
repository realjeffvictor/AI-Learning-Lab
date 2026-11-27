## Repeating until something changes

A `for` loop runs once per item. A **`while`** loop keeps running **as long as a condition is true**. Use it when you do not know in advance how many passes you need.

```python
count = 3
while count > 0:
    print(count)
    count = count - 1
print("liftoff")
```

This prints `3`, `2`, `1` and then `liftoff`. Python checks the condition before every pass. The loop ends the first time the condition is false.

## You must change something

The body has to eventually make the condition false. If it does not, the loop never ends:

```python
while True:
    print("forever")
```

A loop like that is called an **infinite loop**. In the playground on this platform it is stopped after 10 seconds. On a real machine you would press Ctrl+C. When your own program hangs, an unchanged variable in the `while` condition is the first thing to check.

## A worked example: doubling

How many doublings does it take to get from 1 to at least 100?

```python
x = 1
steps = 0
while x < 100:
    x = x * 2
    steps += 1
print(x, steps)    # 128 7
```

The values are 1, 2, 4, 8, 16, 32, 64 and then 128. Seven doublings.

## break: leave the loop now

`break` ends the loop immediately, even if items are left.

```python
for n in [3, 8, 14, 20]:
    if n % 7 == 0:
        print("found", n)
        break
```

This prints `found 14` and never looks at 20. Use `break` when you are searching and have found what you need.

## continue: skip to the next pass

`continue` abandons the current pass and moves on to the next one.

```python
for n in range(1, 6):
    if n % 2 == 0:
        continue
    print(n)
```

This prints `1`, `3` and `5`. The even numbers are skipped.

## Which loop should I use?

- Going through every item of something: `for`.
- Repeating until a condition changes, with no known count: `while`.
- Finding the first match: either, with `break`.

## Reading AI-written loops

Loops are where generated code most often goes wrong quietly: a condition that is never reached, a counter updated in the wrong place, or a `break` inside the wrong `if`. **Verify** by running the loop on a tiny input and tracing it by hand, and ask: *what makes this loop stop?* If you cannot answer that, you do not yet **Own** the code.

## Check yourself

After `count = 0`, then `while count < 3: count += 1`, what does `print(count)` show? And after `for n in range(10): if n == 3: break`, what is `n`?

The answers are `3` and `3`.
