import { Link } from "react-router-dom";

import { ErrorNote, Loading } from "../components/StateMessage";
import { useProgressSummary } from "../features/curriculum/hooks";
import { ProgressTrace } from "../features/curriculum/ProgressTrace";
import { MasterySection } from "../features/exercises/MasterySection";
import { StudyPlanSection } from "../features/ai/StudyPlanSection";
import { AchievementsSection } from "../features/projects/AchievementsSection";
import type { Competency } from "../features/curriculum/types";
import { formatDuration } from "../lib/format";

const CATEGORY_TITLE: Record<Competency["category"], string> = {
  A: "A. Deep technical understanding",
  B: "B. AI-assisted implementation",
  C: "C. Engineering judgment",
};

export function ProgressPage() {
  const summary = useProgressSummary();
  if (summary.isPending) return <Loading label="Loading progress" />;
  if (summary.isError) return <ErrorNote error={summary.error} />;
  const data = summary.data;

  return (
    <div>
      <p className="font-mono text-xs uppercase tracking-widest text-ink-muted">Progress</p>
      <h1 className="mt-2 font-serif text-3xl">Your learning so far</h1>
      <p className="mt-2 font-mono text-sm text-ink-muted">
        {data.lessons_completed} lessons completed. {formatDuration(data.time_spent_seconds)} spent in lessons.
      </p>

      <h2 className="mb-1 mt-10 font-mono text-xs uppercase tracking-widest text-ink-muted">By course</h2>
      <ul className="divide-y divide-rule border-y border-rule">
        {data.courses.map((course) => (
          <li key={course.id} className="grid gap-2 py-3 md:grid-cols-[minmax(0,1fr)_18rem_10rem] md:items-center">
            <Link to={`/courses/${course.slug}`} className="font-serif text-lg hover:text-signal">
              {course.title}
            </Link>
            <ProgressTrace
              published={course.published_lesson_count}
              completed={course.completed_lesson_count}
              planned={course.planned_lesson_count}
            />
            <span className="font-mono text-xs text-ink-muted">
              {course.completed_lesson_count}/{course.published_lesson_count} written
            </span>
          </li>
        ))}
      </ul>

      <AchievementsSection />

      <StudyPlanSection />
      <MasterySection />

      <h2 className="mb-1 mt-10 font-mono text-xs uppercase tracking-widest text-ink-muted">Concept exposure</h2>
      <p className="max-w-2xl text-sm text-ink-muted">
        Counts how many completed lessons covered each concept. This shows what you have studied, not how well you know
        it. Skill levels will come from graded exercises.
      </p>
      {data.competencies.length === 0 ? (
        <p className="mt-4 text-sm text-ink-muted">Complete a lesson and the concepts it covers will appear here.</p>
      ) : (
        (["A", "B", "C"] as const).map((category) => {
          const items = data.competencies.filter((item) => item.category === category);
          if (items.length === 0) return null;
          return (
            <section key={category} className="mt-6">
              <h3 className="font-serif text-lg">{CATEGORY_TITLE[category]}</h3>
              <ul className="mt-1 divide-y divide-rule border-y border-rule font-mono text-sm">
                {items.map((item) => (
                  <li key={item.slug} className="grid grid-cols-[minmax(0,1fr)_auto] gap-3 py-2">
                    <span className="font-sans">{item.name}</span>
                    <span className="text-ink-muted">
                      {item.lessons_completed} {item.lessons_completed === 1 ? "lesson" : "lessons"}
                    </span>
                  </li>
                ))}
              </ul>
            </section>
          );
        })
      )}
    </div>
  );
}
