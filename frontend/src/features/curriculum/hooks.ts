import { useQuery, type QueryClient } from "@tanstack/react-query";

import { fetchCourse, fetchCourses, fetchLesson, fetchProgressSummary } from "./api";

export function useCourses() {
  return useQuery({ queryKey: ["courses"], queryFn: ({ signal }) => fetchCourses(signal) });
}

export function useCourse(slug: string | undefined) {
  return useQuery({
    queryKey: ["course", slug],
    queryFn: ({ signal }) => fetchCourse(slug as string, signal),
    enabled: Boolean(slug),
  });
}

export function useLesson(course?: string, module?: string, lesson?: string) {
  return useQuery({
    queryKey: ["lesson", course, module, lesson],
    queryFn: ({ signal }) => fetchLesson(course as string, module as string, lesson as string, signal),
    enabled: Boolean(course && module && lesson),
  });
}

export function useProgressSummary() {
  return useQuery({ queryKey: ["progress", "summary"], queryFn: ({ signal }) => fetchProgressSummary(signal) });
}

/** Call after anything that changes enrollment or progress so every view refetches. */
export function invalidateProgressQueries(queryClient: QueryClient): Promise<unknown> {
  return Promise.all([
    queryClient.invalidateQueries({ queryKey: ["courses"] }),
    queryClient.invalidateQueries({ queryKey: ["course"] }),
    queryClient.invalidateQueries({ queryKey: ["lesson"] }),
    queryClient.invalidateQueries({ queryKey: ["progress"] }),
  ]);
}
