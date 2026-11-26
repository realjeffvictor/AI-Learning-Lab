import type { ConceptOption } from "./types";
import { toggle } from "./utils";

const TITLES = { A: "A. Deep understanding", B: "B. AI-assisted", C: "C. Engineering judgment" } as const;

export function ConceptPicker({
  options,
  selected,
  onChange,
}: {
  options: ConceptOption[];
  selected: string[];
  onChange: (next: string[]) => void;
}) {
  return (
    <div className="space-y-3">
      {(["A", "B", "C"] as const).map((category) => {
        const group = options.filter((item) => item.category === category);
        if (group.length === 0) return null;
        return (
          <fieldset key={category}>
            <legend className="font-mono text-xs text-ink-muted">{TITLES[category]}</legend>
            <div className="mt-1 grid gap-x-4 gap-y-1 sm:grid-cols-2">
              {group.map((item) => (
                <label key={item.slug} className="flex cursor-pointer items-start gap-2 text-sm">
                  <input
                    type="checkbox"
                    className="mt-1"
                    checked={selected.includes(item.slug)}
                    onChange={() => onChange(toggle(selected, item.slug))}
                  />
                  <span>{item.name}</span>
                </label>
              ))}
            </div>
          </fieldset>
        );
      })}
    </div>
  );
}
