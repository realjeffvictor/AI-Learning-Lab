import Markdown from "react-markdown";

/** Renders lesson Markdown. react-markdown ignores raw HTML and strips unsafe URLs by default. */
export function LessonMarkdown({ source }: { source: string }) {
  return (
    <div className="lesson-prose">
      <Markdown
        components={{
          a({ href, children }) {
            const external = typeof href === "string" && /^https?:\/\//.test(href);
            return (
              <a href={href} target={external ? "_blank" : undefined} rel={external ? "noopener noreferrer" : undefined}>
                {children}
              </a>
            );
          },
        }}
      >
        {source}
      </Markdown>
    </div>
  );
}
