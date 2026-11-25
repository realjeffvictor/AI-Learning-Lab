import { useMutation } from "@tanstack/react-query";
import { useState, type FormEvent } from "react";

import { Button } from "../components/Button";
import { Field } from "../components/Field";
import { updateProfile } from "../features/auth/api";
import { useAuth } from "../features/auth/AuthContext";
import type { ExperienceLevel } from "../features/auth/types";
import { describeError } from "../lib/api/messages";

const LEVELS: ExperienceLevel[] = ["beginner", "intermediate", "advanced"];

export function ProfilePage() {
  const { user, replaceUser } = useAuth();
  const [name, setName] = useState(user?.profile.display_name ?? "");
  const [bio, setBio] = useState(user?.profile.bio ?? "");
  const [level, setLevel] = useState<ExperienceLevel>(user?.profile.experience_level ?? "beginner");

  const save = useMutation({ mutationFn: updateProfile, onSuccess: (updated) => replaceUser(updated) });
  if (!user) return null;

  function onSubmit(event: FormEvent) {
    event.preventDefault();
    save.mutate({ display_name: name, bio, experience_level: level });
  }

  return (
    <div className="max-w-xl">
      <p className="font-mono text-xs uppercase tracking-widest text-ink-muted">Profile</p>
      <h1 className="mt-2 font-serif text-3xl">Your profile</h1>
      <p className="mt-2 text-ink-muted">Your experience level will tune how the AI tutor explains things.</p>
      <form onSubmit={onSubmit} className="mt-8 flex flex-col gap-4">
        <Field label="Display name" name="display_name" maxLength={80} required value={name} onChange={(e) => setName(e.target.value)} />
        <div className="flex flex-col gap-1">
          <label htmlFor="bio" className="font-mono text-xs uppercase tracking-widest text-ink-muted">
            Bio
          </label>
          <textarea
            id="bio"
            rows={4}
            maxLength={500}
            value={bio}
            onChange={(e) => setBio(e.target.value)}
            className="rounded-md border border-rule bg-surface px-3 py-2 text-base text-ink"
          />
        </div>
        <div className="flex flex-col gap-1">
          <label htmlFor="level" className="font-mono text-xs uppercase tracking-widest text-ink-muted">
            Experience level
          </label>
          <select
            id="level"
            value={level}
            onChange={(e) => setLevel(e.target.value as ExperienceLevel)}
            className="rounded-md border border-rule bg-surface px-3 py-2 text-base text-ink"
          >
            {LEVELS.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </div>
        {save.isError && (
          <p role="alert" className="text-sm text-danger">
            {describeError(save.error)}
          </p>
        )}
        {save.isSuccess && <p className="text-sm text-ok">Saved.</p>}
        <div>
          <Button type="submit" disabled={save.isPending || !name.trim()}>
            {save.isPending ? "Saving..." : "Save profile"}
          </Button>
        </div>
      </form>
    </div>
  );
}
