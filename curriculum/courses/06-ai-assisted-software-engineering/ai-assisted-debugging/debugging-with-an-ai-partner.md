## An assistant is a good rubber duck, not an oracle

Debugging is finding out why a program does something other than what you expected. An AI assistant can help a lot, if you use it as a partner who proposes ideas that **you** then test.

## Do the groundwork first

1. **Reproduce it.** Find an input that fails every time. A bug you cannot repeat cannot be fixed or checked.
2. **Shrink it.** Cut the input and the code down until the smallest version still fails.
3. **Read the error.** The last line says what went wrong, and the lines above it say where. Many errors are explained completely by reading them slowly.

## What to give the assistant

The more precise the report, the better the help:

- The **full** error message, including the traceback.
- The **smallest code** that shows the problem.
- What you **expected**, and what **actually happened**.
- What you have already tried.

"It does not work" gives it almost nothing to work with.

## Ask for hypotheses, not just a fix

Instead of "fix this", ask: *"What are the three most likely causes, and how could I test each one?"* Then run those tests yourself. This keeps you learning and stops you applying a confident fix to the wrong problem.

## Symptom versus root cause

Take this function meant to add up the numbers from 1 to `n`:

```python
def sum_to(n):
    total = 0
    for i in range(n):
        total += i
    return total
```

`sum_to(5)` returns `10`, but you expected `15`. The **symptom** is a wrong total. A shallow fix is to add `n` at the end, which makes `sum_to(5)` correct and quietly breaks `sum_to(0)`. The **root cause** is that `range(n)` produces 0 to `n - 1`, so the loop starts at the wrong place and stops one short. The right fix is `range(1, n + 1)`.

Always ask: *why* did this happen, not only *where* did it show up?

## Beware fixes that hide the problem

Assistants sometimes make an error disappear instead of solving it, for example by wrapping code in `try / except: pass`, deleting a check, or returning a default value. The error message vanishes, and the bug is still there. If a fix makes the problem go quiet, ask what it did with the failing case.

## After the fix

- Rerun the **original failing input** and see that it now works.
- Rerun your other tests to check you did not break something else.
- Understand **why** it works. If you cannot explain the fix, you do not own it yet.
- Keep the failing input as a test so the bug cannot quietly return.

## When you are stuck

Explain the problem out loud, or in writing, as if to someone who knows nothing. This works because writing it down forces you to state what you assume, and the bug often lives in an assumption. An assistant can be the listener, but a rubber duck on your desk works too.

## Check yourself

You ask an assistant about a crash and it suggests adding `try: ... except: pass`. List two things that are wrong with that suggestion.
