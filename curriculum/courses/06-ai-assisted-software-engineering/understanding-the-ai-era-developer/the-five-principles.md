## Faster, but still responsible

AI tools can write code, explain errors and draft tests in seconds. That changes how developers work. It does not change who is responsible for the software. If the code you ship is wrong, "the AI wrote it" is not an answer anyone accepts.

Five principles keep you in charge.

## The five principles

**Understand.** Know the concepts, the architecture and the way data flows through your system. You cannot give good instructions or judge good output about something you do not understand.

**Direct.** Give the AI a clear goal, the relevant context and your constraints. A vague request gets a vague answer, and a precise one gets something you can use.

**Build.** Let AI do the repetitive work: boilerplate, routine code, first drafts. This is where the speed comes from.

**Verify.** Read, run and test what it produces. Generated code looks confident whether it is right or wrong.

**Own.** You understand the system, you can change it, and you are accountable for it. If you could not maintain it without the AI, you do not own it yet.

## Verify in practice

An assistant might offer this:

```python
def average(numbers):
    return sum(numbers) / len(numbers)
```

It looks correct, and for `[2, 4, 6]` it returns `4.0`. Now ask what happens with an empty list. `sum([])` is `0` and `len([])` is `0`, so Python raises `ZeroDivisionError: division by zero`.

You only spot that if you understand the code, and you only keep it from reaching users if you test the edge cases. Both come from the principles, not from the tool.

## Three kinds of competence

This platform trains three things, and treats them differently:

- **Deep understanding** of the fundamentals: logic, data, algorithms, databases, APIs, security, testing. You learn these yourself, and you are assessed without AI help.
- **AI-assisted implementation:** using AI for boilerplate, explanations, tests and documentation, quickly and well.
- **Engineering judgment:** choosing technologies, weighing trade-offs, reviewing generated code and diagnosing root causes.

Speed at producing code is not what we measure. We measure whether you understand and can maintain what you built.

## Check yourself

Pick one thing you used AI for recently. Which of the five principles did you apply, and which did you skip? Write one sentence for each. The principle you skipped is the one to practise next.
