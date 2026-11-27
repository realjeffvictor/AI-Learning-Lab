## What you are actually talking to

An AI coding assistant is built on a **language model**. It has learned patterns from a very large amount of text and code, and when you give it a prompt it produces the text that is most likely to follow. That is a powerful trick. It is also the root of every strength and weakness in this lesson.

It does **not** look up the one correct answer. It does **not** run your code unless it has been given a tool that does. It produces something that *looks* right.

## What assistants are good at

- Writing routine code and boilerplate quickly.
- Explaining unfamiliar code, error messages and concepts.
- Suggesting alternatives you had not thought of.
- Drafting tests, comments and documentation.
- Translating an idea from one language or style to another.

## Where they go wrong

- **Plausible but wrong.** The tone is the same whether the answer is right or wrong. A confident explanation proves nothing.
- **Invented things.** Assistants sometimes use functions, options or whole packages that do not exist. This is often called *hallucination*.
- **Out-of-date knowledge.** What it learned has a cut-off, so it may suggest old ways of doing things.
- **Limited context.** It can only consider a limited amount of text at once, called its **context window**. Anything you did not include, it cannot see, and in a long conversation early details can be lost.
- **Different answers each time.** Asking the same question twice can give different code.
- **It does not know your situation.** Your data, your users and your constraints are invisible unless you say them.

## Three ways you will meet one

1. **Chat:** you describe a problem and read the answer.
2. **Inline suggestions:** the editor proposes the next lines as you type.
3. **Agents:** the assistant can edit files and run commands for you.

The more an assistant can *do*, the more important your review becomes. An agent that edits many files can break many things at once. Whatever you use, keep your work in **version control** so you can see exactly what changed and undo it, and read every change before you accept it.

## Protect what you paste

Treat a chat box like a message to a stranger:

- Never paste passwords, API keys, tokens or private keys.
- Be careful with personal data, customer data and code your employer or client owns. Check the rules that apply to you and the provider's data policy.
- Replace real values with placeholders such as `YOUR_API_KEY` before you paste.

If a secret was pasted by accident, treat it as leaked and replace it at the source.

## The loop that keeps you in charge

The five principles from the first lesson of this track turn into a working loop:

1. **Understand** the problem well enough to explain it yourself.
2. **Direct** the assistant with a clear goal, context and constraints.
3. **Build** by letting it draft the routine parts.
4. **Verify** by reading, running and testing the result.
5. **Own** what you keep: you must be able to explain and maintain it.

Skipping *Verify* is how bugs and security holes get in. Skipping *Own* is how a project becomes impossible to change a month later.

## Check yourself

Pick the last time you used an AI tool. Which of the five steps did you skip? Write one sentence about what you would do differently.
