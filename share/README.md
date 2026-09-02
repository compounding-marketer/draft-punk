# Draft Punk

A Markdown editor that runs entirely in your browser. One HTML file, no install,
no account, no server. Your files never leave your computer.

## Use it

Open `draft-punk.html` in **Chrome, Edge, Arc, or Brave**, then either:

- Click **Open File…** (or press `⌘O`) and pick a `.md` file, or
- **Drag a Markdown file** onto the window

Edit it, press `⌘S`, and the changes are written straight back to the original
file on your disk.

## What's in it

- **Read / Edit** — the same formatted view, editable in place. No split panes,
  no raw-markdown pane. `⌘E` toggles.
- **Formatting toolbar** plus `⌘B` bold, `⌘I` italic, `⌘K` link. Typing `# `,
  `- ` or `> ` at the start of a line formats as you go.
- **Sticky notes** — `⌘J` drops one on the page, anchored to the document so it
  stays beside the paragraph you put it next to. Five colours, drag to move,
  resize from the corner, and **✎ to scribble on them freehand**. `👁` hides them all.
- **Three themes** in the header dropdown — Draft Punk (lime, editorial),
  Blueprint (electric blue, bold sans, graph-paper grid), and Manuscript
  (warm paper, serif, built for long reading). Each has its own fonts and shapes.
- **Dark and light** are separate, switched with `☾` — six looks in total.
  Every combination clears WCAG AA contrast.
- **Recent files** genuinely reopen — the browser remembers the file itself,
  not just its name.

## Browser support

Saving back to the original file uses the File System Access API:

| Browser | Open | Edit | Save to original file |
|---|---|---|---|
| Chrome / Edge / Arc / Brave | yes | yes | yes |
| Safari / Firefox | yes | yes | downloads a copy instead |

## Privacy

There is no backend and your file never leaves your computer — it is read and
written directly by the browser, never sent anywhere. Sticky notes live in your
browser's local storage.

Two honest caveats. The page requests typefaces from **Google Fonts**; if that's
blocked, it falls back to system fonts and works exactly the same. And if you're
using the **hosted** version rather than a downloaded copy, GitHub serves the page
and logs that request the way any website does. Neither one can see your file —
that stays local either way. Download the file if you'd rather make no network
request at all.
