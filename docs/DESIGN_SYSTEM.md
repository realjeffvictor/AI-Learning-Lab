# Design System: "Lab Notebook meets Terminal"

## Direction
A technical workbench with an editorial feel: dense, calm, precise. Paper-toned surfaces and ink text for reading;
a true-dark code environment for tools. One signal accent. Hairline rules instead of heavy cards. Varied layouts per screen.
Avoid: purple/blue gradients, glassmorphism, blobs, brain art, uniform card grids, glowing borders, stock illustrations.

## Signature motifs
- Margin-note layout for lessons (prose column + annotation gutter for definitions, warnings, AI tips).
- Principle glyphs U D B V O shown as a small monospace ledger on lessons, exercises and projects.
- Ruled/graph-paper hairlines as section dividers; line numbers as a recurring visual element.
- Progress shown as a "trace" (stepped line) rather than donut charts.

## Color tokens (light / dark)
--paper:        #F6F3EC / #14130F      (app background)
--surface:      #FFFFFF / #1B1A16      (panels)
--surface-sunk: #ECE8DE / #100F0C      (wells, code gutters)
--ink:          #1C1B17 / #ECE8DC      (primary text)
--ink-muted:    #5E5A4F / #A29D8E
--rule:         #D9D3C4 / #2C2A23      (hairlines)
--signal:       #D9480F / #FF7A3D      (single accent: actions, active state)
--signal-ink:   #FFFFFF / #1A0A00
--ok:           #2F7D4F / #5BC184
--warn:         #B7791F / #E0A93B
--danger:       #B3261E / #F2786F
--info:         #2A6F8F / #6FB4D4
Code editor theme: custom "labdark" and "labpaper" Monaco themes derived from these tokens.
Rules: accent used sparingly (one primary action per view); contrast at least WCAG AA; color is never the only status signal.

## Typography
- UI: IBM Plex Sans (400/500/600). Code and data: JetBrains Mono. Lesson prose and display headings: Source Serif 4.
- Scale (rem): 0.75 / 0.8125 / 0.9375 / 1 / 1.125 / 1.375 / 1.75 / 2.5. Line-height 1.5 body, 1.2 headings.
- Self-host fonts (privacy, performance, offline reliability).

## Spacing, shape, elevation
- 4px base: 4, 8, 12, 16, 24, 32, 48, 64. Radius: 2 / 4 / 8 (default 4; no pill-everything).
- Borders over shadows. Shadow only for floating layers (menus, dialogs). Max one elevation level in the workspace.
- Motion: 120 to 200ms, ease-out; only for state change, focus, panel transitions; honor prefers-reduced-motion.

## Layout rules
- App shell: slim top bar + collapsible left rail (icons + labels). Content max-width 1200 for reading screens; full-bleed for workspaces.
- Lesson workspace: [lesson nav] | [lesson content] | [editor over output] | [assistant drawer], resizable; tabs on tablet/mobile.
- Mobile: lessons, progress, quizzes fully usable; coding supported but flagged as best on desktop.

## Component conventions
Button (primary/secondary/ghost/danger, sizes), IconButton, Input/Textarea/Select, Tabs, Panel/SplitPane, Table (dense),
Badge/Status, Tooltip, Dialog, Toast, CodeBlock, OutputConsole, ProgressTrace, PrincipleLedger, EmptyState, ErrorState, Skeleton.
Icons: Lucide, one stroke width. All components keyboard accessible with visible focus rings in --signal.

## Screen inventory
Landing, Register, Login, Dashboard, Curriculum overview, Course detail, Module, Lesson workspace, Python playground,
AI tutor, AI dev-assistant workspace, Project workspace, Progress/competency, Profile, Puzzles/Games hub, Results and
recommendations, Instructor dashboard, Admin dashboard (+ content editors), Notifications.
