## The scenario

A teammate asked an AI assistant for helper functions for a small user-management script. This is what came back. It looks tidy and confident. Your job is to review it before it is merged.

```python
def average(numbers):
    return sum(numbers) / len(numbers)


def find_user(users, name):
    for user in users:
        if user["name"] == name:
            return user
    return None


def save_password(db, username, password):
    db.execute(
        f"INSERT INTO users (name, password) VALUES ('{username}', '{password}')"
    )
```

## What to do

Write a review of this code in the documentation box. A good review:

- Lists each problem separately, most serious first.
- Says what actually goes wrong, and with what input.
- Describes the fix in your own words. You do not need to write the final code.
- Says how you would test the fix, including an edge case.
- Ends with the instruction you would give the AI assistant to produce a better version.

You do not need to run the code, but you may. Python's standard library is enough to try the first two functions.

## How this is assessed

This is a reviewed task. Nothing is scored automatically. A reviewer reads your review and scores your understanding, the quality of your reasoning, how you would verify the fixes, and whether you took ownership of the code instead of trusting it.

In the reflection box, say what you would do differently the next time an assistant gives you code like this.
