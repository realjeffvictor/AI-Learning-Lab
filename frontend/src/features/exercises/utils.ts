/** Returns a copy of `items` with the element at `index` moved by one position. Out-of-range moves change nothing. */
export function moveItem<T>(items: readonly T[], index: number, delta: -1 | 1): T[] {
  const target = index + delta;
  if (index < 0 || index >= items.length || target < 0 || target >= items.length) return [...items];
  const next = [...items];
  const [moved] = next.splice(index, 1);
  next.splice(target, 0, moved as T);
  return next;
}

export function allAnswered(questionIds: readonly string[], answers: Record<string, number | undefined>): boolean {
  return questionIds.every((id) => answers[id] !== undefined);
}

export function percent(correct: number, total: number): number {
  return total === 0 ? 0 : Math.round((100 * correct) / total);
}
