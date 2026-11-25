import { useEffect } from "react";

import { addLessonTime } from "./api";

const FLUSH_EVERY_SECONDS = 30;

/** Counts seconds the lesson tab is visible and reports them in batches. The server decides how much to credit. */
export function useLessonTimer(lessonId: string | null, active: boolean): void {
  useEffect(() => {
    if (!lessonId || !active) return;
    let pending = 0;

    const flush = () => {
      const seconds = Math.min(pending, 120);
      pending = 0;
      if (seconds >= 1) void addLessonTime(lessonId, seconds).catch(() => undefined);
    };

    const timer = window.setInterval(() => {
      if (document.visibilityState === "visible") pending += 1;
      if (pending >= FLUSH_EVERY_SECONDS) flush();
    }, 1000);

    return () => {
      window.clearInterval(timer);
      flush();
    };
  }, [lessonId, active]);
}
