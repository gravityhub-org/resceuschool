#import "typst/slides.typ": *

#show: phys4430-slides.with(
  course: "",
  week: "Gravitational-wave lensing · Lecture 1",
  title: "Theoretical minimum",
)

#title-slide([Gravitational-wave lensing], subtitle: [theoretical minimum])



// =============================================================================
// SLIDE RULES — keep at END of every deck
// (lecture1.typ / lecture2.typ — always both).
// Canonical copy: lecture_notes/common/typst/slide_rules_footer.typ
// When rules change: update that file, then replace this block in each deck.
// Every week: lecture1.typ + lecture2.typ matching lecture_plan (never combined main.typ).
// =============================================================================
//
// FRAMEWORK
// - Dark theme: near-black bg (#121212), off-white text (#F2F2F2), soft cyan accent.
//   Font: Atkinson Hyperlegible (low-vision letter distinction). Larger type + open leading.
//   Figures sit on a light panel so dark-ink plots stay readable.
// - Typst only. Import: #import "typst/slides.typ": *
//   (presentation/typst -> ../../common/typst; `typst watch lecture1.typ`)
// - #show: phys4430-slides.with(…)  — footer = page n/N ONLY (no course chrome)
// - One constructor call = one PDF page (animation-slide = one page per frame)
// - No bullet reveals. Margins ≥ ~0.7 cm horizontal.
// - Content grid is height-bounded: figures MUST use
//     image(..., width: 100%, height: 100%, fit: "contain")
//   so tall art cannot overflow the page.
//
// TOPIC ARC (every *science* topic)
// 1. title-slide — transition
// 2. Observational/physics puzzle — real picture + motivating question (BEFORE jargon)
// Then in order (do not reorder):
//   puzzle/history → concept → technical illustration → math → example
//   → broader context → significance
// Mnemonic: puzzle → concept → picture → math → example → generalise → significance
// New concepts: check C&O extract first; mirror its introduction path; then supplement.
// (No “C&O” / “Carroll” on the student slide — book anchors in // only.)
//
// Logistics / syllabus (Week 1 opener): one Welcome + one combined content slide.
// Must not: title-slide per AI / help / schedule / “exciting now” micro-topic.
//
// 1. title-slide(title, subtitle: …)
// 2. figure-slide(title, figure, credit: …)     — title + still; credit if third-party
// 3. two-figure-slide(title, fig-a, fig-b, credit-a: …, credit-b: …)
//      — left fig | right fig (no bullets); shared credit: if both credit-a/b omitted
// 4. columns-slide(title, figure, credit: …)[ ] — ~55% fig | ~45% text (text VERTICALLY CENTERED)
// 5. two-figure-columns-slide(title, fig-a, fig-b, credit: …)[ ]
//      — two figs LEFT (side-by-side; stacked: true for vertical) | text RIGHT
// 6. mc-question-slide(title, figure, (…,), credit: …)[ context or [] ]
// 7. mc-answer-slide(title, figure, answer, credit: …)[ bullets ]
// 8. derivation-slide(title)[ guided steps ]
// 9. two-text-columns-slide(title, left, right) — two text columns (syllabus / compare)
// 10. movie-slide(title, poster, "….mp4", credit: …) — play MP4; filename at bottom
// 11. animation-slide(title, (frame1, …), credit: …)  — flipbook fallback (≤4 frames)
// 12. office-qa-slide() — LAST content slide: SC347 photo + ask questions (before this footer)
//
// STUDENT-FACING TEXT (strict)
// - Define every new term: meaning, then a concrete example (baseline, p, parsec, …).
// - Talk to the reader about physics — never narrate the slide/section/deck
//   (“why this section matters”, “in this slide we…”, “this chapter will cover…”,
//   “why the course looks this way”). See lecture-notes-prose.mdc Voice.
// - Self-contained: gloss people, named stars/objects, and missions on first use
//   (who/what + why here). See lecture-notes-prose.mdc Self-contained.
// - No unexplained metaphors. Question titles students can parse.
// - Full-bleed: no pedagogical caption under the figure.
// - Web/third-party media: REQUIRED short muted credit via credit: […]
//   (author/org + venue). Full URL/license still in figures/external/ATTRIBUTION.txt.
//   Course-made plots/TikZ: no credit line needed.
// - Long text → short bullets; derivations name each symbol before use.
// - Text on split slides is VERTICALLY CENTERED (keep ≤ ~4 short bullets so clip does not chop).
//
// FIGURES & MEDIA
// - Prefer week figures/; symlink figures -> ../figures
// - LARGE FILES → DVC (≥100 KiB / any video / frame dirs)
// - New web/YouTube: weekNN_media.json → fetch_media.py → dvc repro;
//   ATTRIBUTION.txt + on-slide credit: […]
//
// WHEN ADDING A SLIDE
// - Matching constructor; ≤ ~4 bullets; define+example for new terms; no meta text.
// - Logistics: one Welcome + one combined slide (no title-slide per AI/help/schedule).
// - animation-slide ≤ 4 frames (constructor caps); avoid movie-page floods.
// - Text vertically centered in columns; ~55/45; no right-edge glyph clip.
// - Third-party image/movie → credit: on the constructor.
// - End every deck with #office-qa-slide() immediately before this RULES block.
// - Leave this RULES block at the end of the file.
// =============================================================================
