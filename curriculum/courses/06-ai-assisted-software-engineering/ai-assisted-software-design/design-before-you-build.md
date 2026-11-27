## Decide the shape before you generate the code

Assistants make it tempting to start typing prompts and see what comes back. For anything bigger than one function, that produces a pile of code that works in pieces and fits together badly. A little design first is much cheaper than rewriting later.

## Start with the data

Most programs are about some data and what happens to it. Decide what the data looks like before you write a line. For a to-do list, one task might be:

```python
task = {"title": "write report", "done": False}
```

and the list is a list of those. Once the shape is settled, the functions follow: *add* a task, *mark one done*, *list what is still pending*. If you ask an assistant to write these without fixing the data shape first, each piece may invent its own.

## Name the functions and what goes in and out

Write down the **interface** of each piece before any of its code: its name, what it takes, what it returns. For example:

- `add_task(tasks, title)` returns a new list with the task added.
- `complete_task(tasks, title)` returns a new list with that task marked done.
- `pending(tasks)` returns the titles of tasks not yet done.

Each is small, has one job, and can be tested alone. Hand the interface to an assistant, and ask it to fill in one function at a time.

## Prefer functions that do not change their inputs

A **pure** function gives the same result for the same input and does not modify what it was given. They are easy to test and easy to reason about:

```python
def add_task(tasks, title):
    return tasks + [{"title": title, "done": False}]
```

The original list is untouched, and the result is a new list. Compare a version that does `tasks.append(...)` and changes the caller's list. That one is quicker to write and harder to trust.

## Ask for alternatives and trade-offs

An assistant will happily give you its first idea. Ask for more:

> Suggest two different ways to structure this, and compare them on simplicity, how easy they are to change, and what could go wrong.

You will often find the simpler option is the better one. Then you decide, and say why. Choosing between designs is **engineering judgment**, and it is the part of the job that remains yours.

## Write the check before the code

Write down two or three examples of what the finished piece should do, as `assert` lines or plain sentences. Then you can tell when generated code is right. This is the "example" step from the prompting lesson, applied to design:

```python
assert pending([{"title": "a", "done": True}, {"title": "b", "done": False}]) == ["b"]
```

## Keep the steps small

Build in slices you can verify: the data and one function, check it, then the next. If an assistant produces the entire application in one go, you now have something you did not design, cannot easily check, and probably cannot explain.

## Write the plan down

A short note covering what the program does, the data shape, the functions and the choices you made, kept alongside the code, helps your future self and any assistant you paste it to. It is the start of the documentation you will write in a later lesson.

## Check yourself

Why is it a good idea to decide the shape of the data before asking an assistant to write functions that use it? What does a pure function make easier?
