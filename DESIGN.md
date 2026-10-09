---
name: Generation studio
description: A minimal prompt instrument over a quiet material video loop
colors:
  signal: "#9e1515"
  bright: "#e93631"
  canvas: "#040404"
  panel: "#101211"
  settings: "#0b0d0c"
  field: "#151916"
  text: "#eeeeee"
  white: "#ffffff"
  muted: "#a1aaa7"
  line: "#353b39"
  error: "#ffaaa3"
typography:
  body:
    fontFamily: '"FT Overpass", Arial, sans-serif'
    fontSize: "17px"
    lineHeight: 1.7
  prompt:
    fontFamily: '"FT Overpass", Arial, sans-serif'
    fontSize: "24px"
    lineHeight: 1.35
  title:
    fontFamily: '"FT Overpass", Arial, sans-serif'
    fontSize: "24px"
    fontWeight: 400
    letterSpacing: "-0.02em"
  label:
    fontFamily: '"FT Overpass", Arial, sans-serif'
    fontSize: "13px"
rounded:
  composer: "14px"
  settings: "12px"
  button: "7px"
  field: "6px"
  image: "2px"
spacing:
  control-gap: "18px"
  pair-gap: "36px"
  mobile-pair-gap: "24px"
components:
  button-primary:
    backgroundColor: "{colors.signal}"
    textColor: "{colors.white}"
    rounded: "{rounded.button}"
    padding: "15px 20px"
  button-primary-hover:
    backgroundColor: "#ba2420"
  button-secondary:
    textColor: "{colors.text}"
    rounded: "{rounded.field}"
    padding: "9px 12px"
  input:
    backgroundColor: "{colors.field}"
    textColor: "{colors.text}"
    rounded: "{rounded.field}"
    padding: "11px 12px"
  composer:
    backgroundColor: "{colors.panel}"
    rounded: "{rounded.composer}"
    padding: "26px 30px 22px"
---

# Design System: Ask me anything

## Overview

**Creative North Star: "Sculptural light table"**

The implemented interface treats prompting as a sculptural light table: chrome and red-glass artwork establishes the atmosphere, while a central dark composer gives one thought a clear place to become image and text. Outlined Calder lettering supplies the identity; restrained information type keeps controls and saved work readable.

This document records the local build, not creative approval or a published deployment. The review disposition is ship local build. Source evidence is templates/index.html, static/studio.css and static/studio.js; review captures are .impeccable/review/desktop.png, .impeccable/review/mobile.png and .impeccable/review/paired-result.png.

**Key Characteristics:**
- Sculptural image field with a quiet, central composer.
- Near-black surfaces, white information and restrained signal red.
- Paired artifacts with visible partial-result states.

## Colors

### Primary
Signal red marks the generation button and small empty-state rule. Bright red marks focus, caret, range and progress. Keep these functional accents distinct from the richer red glass inside the artwork.

### Neutral
Canvas black surrounds the image and workspace. Panel, settings and field neutrals separate nested controls through small tonal steps and visible borders. White and near-white carry primary information; muted gray-green carries metadata. Pale error red identifies incomplete or failed requests.

## Typography

The title and signature are outlined Calder SVG artwork, not live display text; preserve their proportions and accessible labels. Information uses locally installed licensed FT Overpass with Arial and generic sans-serif fallback. No font binary is redistributed. Cross-device matching is therefore intentionally conditional on installation.

Generated response text uses the body role with a maximum width of 70ch and preserved line breaks. Result prompts use 22px at 1.35 line height, regular weight and slightly tight tracking; history headings use the title role. Supporting labels vary from 11px metadata to 14px composer labels. At the mobile breakpoint, prompt input becomes 20px and responses 16px.

## Layout

A full-width image hero precedes a centered workspace capped at 1080px and otherwise 90vw. The desktop hero is 600px high, with a left text field and artwork cropped toward the right. The composer overlaps its lower edge by 52px. Desktop settings use two columns (1.15fr / 1fr); saved output uses an image/text grid (1.12fr / 1fr).

At 760px and below, settings and output stack, the hero becomes 560px, the composer overlap becomes 20px and padding tightens. Artwork remains cropped toward 68% horizontally. At 1500px and above the hero is 620px. Output, metadata and download links wrap without fixed-width text columns.

## Elevation & Depth

There are no box shadows. Depth comes from photographic sculpture, dark image gradients, the overlapping composer, small surface-tone changes and thin borders. The prompt remains visibly separate from the artwork.

## Shapes

Softened rectangular controls use the radius tokens; generated images are almost square-cornered. Dividers organize history without enclosing every result in another card. Icons are thin, inline SVG strokes. Preserve the signature and title as outlined vector forms.

## Components

- Primary generation button: red fill, arrow, white text; darker muted fill and waiting cursor while busy. Its label changes to Generating… and returns to Generate both.
- Central composer: large transparent textarea inside a bordered panel, a persistent label and a compact action row.
- Settings disclosure: native details/summary with a rotating chevron, two-column desktop controls and single-column mobile controls.
- Secondary preset button and form fields: quiet borders, dark fields and visible focus rings.
- History navigation and result rows: browser-local count, originating prompt, time, paired output and direct download links. Earlier single-media and partial results remain visible.
- Status/progress: live textual feedback plus a narrow moving red line. Reduced motion disables animation and smooth scrolling.

## Do's and Don'ts

### Do:
- Do retain one central prompt and one primary generation action.
- Do keep image and text associated under the originating prompt.
- Do preserve visible focus, readable status messages and partial results.
- Do use the installed licensed Overpass when available and the explicit Arial fallback elsewhere.

### Don't:
- Don't add a custom cursor or cursor-reactive particles.
- Don't turn generated imagery into an obstruction to the prompt or settings.
- Don't redistribute the Overpass binary while redistribution rights remain unresolved.

## October 8 minimal motion revision

Sam requested the headline/tagline removed and prompt/settings as the primary surface. Full-viewport red-black textured video generated on free Hugging Face, silent forward-only loop with a short cross-dissolve at the seam, ambient canvas particles behind opaque controls. Native cursor, persistent motion pause control, reduced-motion and hidden-tab pausing. Mobile settings and result pairs stack; Generate both fills the narrowest viewport.


### Continuous texture revision — approved
The generated source has no convincing natural join. Background rebuilt from a source frame using travelling spatial waves with a 15-second exact period. No reverse, cross-dissolve, or opacity changes. Phase and velocity match at the wrap. Existing particle layer, controls and reduced-motion behavior retained. Sam approved the working preview and authorized publication.
