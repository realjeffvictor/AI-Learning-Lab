## Programs are instructions

A program is a list of instructions that a computer follows exactly, in order. The computer does not guess what you meant. If an instruction is vague or wrong, it does the wrong thing, quickly and without complaint.

Programming is the work of breaking a problem into steps precise enough for a machine to follow.

## A recipe, but stricter

A recipe can say "add salt to taste". A computer cannot taste. It needs an exact amount and an exact moment in the sequence.

Take this problem: *find the largest number in a list.* In plain steps:

1. Remember the first number as the biggest seen so far.
2. Look at each remaining number, one at a time.
3. If it is bigger than the biggest so far, remember it instead.
4. When the numbers run out, the one you remembered is the answer.

A list of steps like this is an **algorithm**. Turning it into a language the computer understands is **coding**. The thinking comes first, and the coding is the translation.

## Why the steps matter more than the syntax

Syntax is the grammar of a language, and you can look it up. Knowing *what steps solve the problem* is the harder skill, and nobody can look that up for you.

AI tools can translate your steps into code very quickly. They can only help well if you can state the steps, and they can only be trusted if you can check the result. That is the **Understand** principle: you cannot direct or verify what you do not understand.

## Check yourself

Without running anything, follow the algorithm by hand on the list `[3, 9, 4]`. After each step in step 2 and 3, write down what "the biggest seen so far" is.

Your answer should be 3, then 9, then 9. If you got something different, reread the four steps and try again before moving on.
