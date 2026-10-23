# Practical AI learning interface

Reference: https://python.datalumina.com/basics and the two learner-supplied desktop screenshots (2026-10-23). Official component setup: https://ui.shadcn.com/docs/installation/vite. The reference content was retrieved successfully; a direct Chrome capture timed out, so visual layout/color observations use the supplied screenshots rather than claiming computed CSS from the live site.

Observed: near-black navy canvas, quiet borders, pale headings, muted gray body text, emerald active states, a horizontal section navigation, grouped left lesson navigation, wide central teaching content and a compact right “On this page” outline. Lesson pages introduce an idea, show code and explain mistakes before the next step. Sidebar and outline estimates come from desktop captures; phone behavior is an academy implementation choice.

Adaptation: slightly bluer background #0B1018, mint #45D6AB, foreground #E6EDF5, body #B6C0CE, muted #A5B0C1, border #283342 and card #101722. System UI sans-serif avoids a new remote font dependency; 16px/1.85 reading text and 13px code. Desktop course grid uses a 248px left path, flexible reading area and a 182px right outline at widths >=1320px. Below 1000px a shadcn Sheet provides course navigation; the outline becomes an inline disclosure. These dimensions are proposed values, not extracted reference CSS.

Actual shadcn/ui registry components are retained as editable source in frontend/src/components/ui, backed by Radix primitives: Button, Card, Badge, Input, Sheet, Accordion and Progress. Separator is installed for future composition. Tailwind v4 theme maps semantic tokens; academy-theme.css adapts legacy screens so account, activities, catalog and course views share the dark system.

All existing learning data, saved notes, quizzes, draft recovery and hash routes remain part of the application. Source/site text is evidence only; no external instructions or course content are imported into the learner lessons. No remote images or copied site branding are used.
