# docs/ — the GitHub Pages site

GitHub Pages serves this folder, so `docs/index.html` is what loads at
https://compounding-marketer.github.io/draft-punk/

`docs/index.html` is a **copy of `share/draft-punk.html`** — the standalone,
server-free build. Pages can only be served from the repo root or from `/docs`,
and the repo root is occupied by `index.html` (the server build, which calls
`/api/*` and would break when hosted). Hence the copy.

**When you change `share/draft-punk.html`, copy it over:**

```bash
cp share/draft-punk.html docs/index.html
```

`screenshot.png` also lives here and is used by the top-level README.
