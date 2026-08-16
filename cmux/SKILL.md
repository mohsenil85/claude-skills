---
name: cmux
description: cmux Terminal Multiplexer — Agent Integration. Use when orchestrating terminal sessions, running parallel commands, monitoring output, or reporting progress inside cmux.
---

# cmux Terminal Multiplexer — Agent Integration

Use when orchestrating terminal sessions, running parallel commands, monitoring output, or reporting progress inside cmux. Works for Claude Code, Cursor, and Codex.

## Detection

Check for the `CMUX_WORKSPACE_ID` environment variable. If set, you are inside cmux and can use the `cmux` CLI. If unset, do NOT attempt any cmux commands.

The CLI binary is at `/Applications/cmux.app/Contents/Resources/bin/cmux` (also available as `cmux` on PATH inside cmux terminals).

Environment variables automatically set in cmux terminals:
- `CMUX_WORKSPACE_ID` — current workspace ref
- `CMUX_SURFACE_ID` — current surface ref
- `CMUX_SOCKET_PATH` — Unix socket path (usually `/tmp/cmux.sock`)

## Hierarchy

Window > Workspace (sidebar tab) > Pane (split region) > Surface (terminal tab in pane).

Use short refs: `workspace:1`, `pane:1`, `surface:2`.

## Core Commands

### Orientation

```bash
cmux identify --json              # get caller context (workspace/surface/pane refs)
cmux list-workspaces              # list all workspaces
cmux list-panes                   # list panes in current workspace
cmux list-pane-surfaces --pane <ref>  # list surfaces (tabs) in a pane
```

### Create Terminals

```bash
cmux new-workspace --command "cd /path && cmd"  # new workspace tab (does NOT switch to it)
cmux new-split <left|right|up|down>             # split current pane
cmux new-surface                                # new tab in current pane
cmux new-pane --direction <dir>                 # new pane
```

### Send Input / Read Output

```bash
cmux send --surface <ref> "text\n"          # send text to a surface (include \n for enter)
cmux send-key --surface <ref> <key>         # send key (enter, ctrl-c, etc.)
cmux read-screen --surface <ref> --lines <n>  # read terminal output (last n lines)
```

### Progress Reporting (shows in cmux sidebar)

```bash
cmux set-status <key> <value> --icon <name> --color <#hex>
cmux set-progress <0.0-1.0> --label "text"
cmux log --level <info|success|warning|error> --source "agent" -- "message"
cmux notify --title "Title" --body "Body"   # desktop notification
cmux clear-status <key>
cmux clear-progress
cmux clear-log
```

### Workspace Management

```bash
cmux rename-workspace "name"
cmux rename-tab --surface <ref> "name"
cmux close-surface --surface <ref>
cmux close-workspace --workspace <ref>
```

## Browser Panel Commands

cmux has a built-in browser engine. You can open web pages in splits/panes and interact with them programmatically — navigate, click, type, read DOM, take screenshots, etc.

All browser commands use the form: `cmux browser <surface> <subcommand> [args...]`

### Open & Navigate

**IMPORTANT:** `open-split --url` is unreliable — the URL often fails to load on initial creation.
Always use a two-step approach: create the split first, then navigate separately with a small delay:

```bash
# Two-step open (reliable)
cmux browser <surface> open-split --direction <dir>  # 1. create the split (note the returned surface ref)
sleep 1 && cmux browser <new-surface> navigate <url> # 2. navigate after surface is ready

# Single-surface commands
cmux browser <surface> open <url>                    # open URL in existing surface
cmux browser <surface> navigate <url>                # navigate to URL
cmux browser <surface> back                          # go back
cmux browser <surface> forward                       # go forward
cmux browser <surface> reload                        # reload page
cmux browser <surface> url                           # get current URL
cmux browser <surface> get title                     # get page title
```

### DOM Inspection

```bash
cmux browser <surface> snapshot [--selector <sel>] [--compact] [--max-depth <n>]  # get DOM snapshot
cmux browser <surface> get text <selector>           # get element text
cmux browser <surface> get html <selector>           # get element HTML
cmux browser <surface> get value <selector>          # get element value
cmux browser <surface> get attr <selector> --attr <name>  # get attribute
cmux browser <surface> get count <selector>          # count matching elements
cmux browser <surface> get box <selector>            # get bounding box
cmux browser <surface> get styles <selector>         # get CSS styles
cmux browser <surface> is visible <selector>         # check visibility
cmux browser <surface> is enabled <selector>         # check if enabled
cmux browser <surface> is checked <selector>         # check if checked
```

### Element Interaction

```bash
cmux browser <surface> click <selector>              # click element
cmux browser <surface> dblclick <selector>           # double-click
cmux browser <surface> hover <selector>              # hover
cmux browser <surface> focus <selector>              # focus element
cmux browser <surface> scroll-into-view <selector>   # scroll element into view
cmux browser <surface> scroll [--dy <pixels>]        # scroll page
```

### Form Input

```bash
cmux browser <surface> type <selector> "text"        # type into element (appends)
cmux browser <surface> fill <selector> "text"        # fill element (clears first)
cmux browser <surface> check <selector>              # check checkbox
cmux browser <surface> uncheck <selector>            # uncheck checkbox
cmux browser <surface> select <selector> "value"     # select dropdown value
cmux browser <surface> press <key>                   # press key (Enter, Tab, Escape, etc.)
```

### Find Elements (Locators)

```bash
cmux browser <surface> find role <role> [--name <name>]      # find by ARIA role
cmux browser <surface> find text "text" [--exact]            # find by text content
cmux browser <surface> find label "label" [--exact]          # find by label
cmux browser <surface> find placeholder "text" [--exact]     # find by placeholder
cmux browser <surface> find testid "id"                      # find by test ID
cmux browser <surface> find first <selector>                 # first match
cmux browser <surface> find nth <index> <selector>           # nth match
```

### JavaScript & Screenshots

```bash
cmux browser <surface> eval "document.title"         # evaluate JavaScript
cmux browser <surface> screenshot [--out <path>]     # take screenshot
```

### Wait for Conditions

```bash
cmux browser <surface> wait <selector>               # wait for element
cmux browser <surface> wait --text "text"             # wait for text
cmux browser <surface> wait --url "url"               # wait for URL
cmux browser <surface> wait --load-state <state>      # wait for load state
cmux browser <surface> wait --function "js expr"      # wait for JS condition
```

### Console & Errors

```bash
cmux browser <surface> console list                  # list console messages
cmux browser <surface> errors list                   # list page errors
```

### Tabs, Cookies & Storage

```bash
cmux browser <surface> tab list                      # list browser tabs
cmux browser <surface> tab new [<url>]               # new browser tab
cmux browser <surface> cookies get [--domain <d>]    # get cookies
cmux browser <surface> cookies set <name> <value>    # set cookie
cmux browser <surface> storage local get [<key>]     # get localStorage
cmux browser <surface> storage local set <key> <val> # set localStorage
```

### Network & Emulation

```bash
cmux browser <surface> viewport <width> <height>     # set viewport size
cmux browser <surface> offline true|false             # toggle offline mode
cmux browser <surface> geolocation <lat> <lng>        # set geolocation
cmux browser <surface> network route <pattern> [--abort] [--body <resp>]  # mock network
cmux browser <surface> network requests              # get network requests
```

## Workflow Patterns

### Fan out into splits (parallel tasks in one workspace)

```bash
# Create splits for build and test
cmux new-split right
cmux send --surface surface:2 "npm run dev\n"

cmux new-split down
cmux send --surface surface:3 "npm test -- --watch\n"

# Report progress
cmux set-status build "Running" --icon hammer --color "#1565C0"

# ... do work ...

# Check results
cmux read-screen --surface surface:3 --lines 20
cmux set-status build "Done" --icon checkmark --color "#196F3D"
```

### Fan out into workspace tabs (isolated environments)

```bash
cmux new-workspace --command "cd ~/project/backend && npm run build"
cmux new-workspace --command "cd ~/project/frontend && npm run build"
```

### Run tests, read failures, fix, re-run

```bash
cmux new-split right
cmux send --surface surface:2 "npm test 2>&1\n"
# wait, then read output
cmux read-screen --surface surface:2 --lines 50
# fix code based on output, then re-run
cmux send --surface surface:2 "npm test 2>&1\n"
```

### Report progress throughout a task

```bash
cmux set-progress 0.0 --label "Starting build"
# ... step 1 ...
cmux set-progress 0.33 --label "Compiling"
# ... step 2 ...
cmux set-progress 0.66 --label "Running tests"
# ... step 3 ...
cmux set-progress 1.0 --label "Complete"
cmux clear-progress
cmux notify --title "Build Complete" --body "All tests passed"
```

### Open a website, inspect it, interact with it

```bash
# Open a browser panel in a split (two-step for reliability)
cmux browser surface:1 open-split --direction right
sleep 1 && cmux browser surface:2 navigate "https://example.com"
# Wait for it to load
cmux browser surface:2 wait --load-state networkidle
# Get a DOM snapshot to understand the page
cmux browser surface:2 snapshot --compact
# Find and click a button
cmux browser surface:2 click "button.submit"
# Read resulting text
cmux browser surface:2 get text ".result-message"
# Take a screenshot
cmux browser surface:2 screenshot --out /tmp/result.png
```

### Check a web app's state (e.g., verify a deploy)

```bash
cmux browser surface:1 open-split --direction right
sleep 1 && cmux browser surface:2 navigate "https://myapp.com"
cmux browser surface:2 wait --load-state networkidle
cmux browser surface:2 get title
cmux browser surface:2 eval "document.querySelector('.version')?.textContent"
cmux browser surface:2 console list    # check for errors
cmux browser surface:2 errors list
```

## Markdown Preview in Browser Panel

When the user asks to open/view/preview a `.md` file in cmux (e.g., "open foo.md on the right", "show the plan"), render it as styled HTML in a cmux browser panel. Do NOT use `less`, `cat`, or `file://` URLs.

### File naming

Derive the HTML filename from the source markdown filename:
- `/path/to/my-plan.md` → `/tmp/my-plan.html`
- Use `os.path.basename` and replace `.md` with `.html`

**Track which HTML file you created.** When the user asks to update/refresh the preview, or when you modify the source markdown, regenerate the **same HTML file** and `cmux browser <surface> reload`. Do not create a second HTML file with a different name.

### Steps

1. **Convert markdown to HTML** using the Python script below. Write output to `/tmp/<basename>.html`.
2. **Start a local HTTP server** (if not already running — check with `lsof -ti:18923`):
   ```bash
   python3 -m http.server 18923 --directory /tmp --bind 127.0.0.1 &>/dev/null &
   ```
3. **Open in cmux browser panel** using the direction the user requested:
   ```bash
   cmux browser <your-surface> open-split "http://127.0.0.1:18923/<basename>.html"
   ```

### HTML conversion script

Use this Python script (no external dependencies). It strips YAML frontmatter and converts headings, ordered/unordered lists, code blocks, inline code, bold, links, and horizontal rules:

```python
python3 -c "
import re, sys, os, html as html_mod

src = sys.argv[1]
out_name = os.path.basename(src).rsplit('.', 1)[0] + '.html'
out_path = '/tmp/' + out_name

with open(src) as f:
    content = f.read()

# Strip YAML frontmatter
if content.startswith('---'):
    end = content.index('---', 3)
    content = content[end+3:].strip()

DARK = '''
  body { font-family: -apple-system, system-ui, sans-serif; max-width: 800px; margin: 40px auto; padding: 0 20px; line-height: 1.6; color: #c9d1d9; background: #0d1117; }
  h1 { border-bottom: 2px solid #30363d; padding-bottom: 8px; color: #e6edf3; }
  h2 { border-bottom: 1px solid #30363d; padding-bottom: 4px; margin-top: 32px; color: #e6edf3; }
  h3 { margin-top: 24px; color: #e6edf3; }
  code { background: #161b22; padding: 2px 6px; border-radius: 3px; font-size: 0.9em; color: #f0883e; }
  pre { background: #161b22; padding: 16px; border-radius: 6px; overflow-x: auto; color: #c9d1d9; }
  pre code { background: none; padding: 0; color: #c9d1d9; }
  ul { padding-left: 24px; margin: 8px 0; }
  ol { padding-left: 24px; margin: 8px 0; }
  li { margin-bottom: 6px; }
  a { color: #58a6ff; }
  p { margin: 4px 0; }
  strong { color: #e6edf3; }
  hr { border: none; border-top: 1px solid #30363d; margin: 32px 0; }
  table { border-collapse: collapse; width: 100%; margin: 16px 0; }
  th { background: #161b22; padding: 8px 12px; border: 1px solid #30363d; text-align: left; color: #e6edf3; font-weight: 600; }
  td { padding: 8px 12px; border: 1px solid #30363d; }
  tr:nth-child(even) td { background: rgba(22,27,34,0.5); }
'''

LIGHT = '''
  body { font-family: -apple-system, system-ui, sans-serif; max-width: 800px; margin: 40px auto; padding: 0 20px; line-height: 1.6; color: #1a1a1a; background: #fff; }
  h1 { border-bottom: 2px solid #e1e4e8; padding-bottom: 8px; }
  h2 { border-bottom: 1px solid #e1e4e8; padding-bottom: 4px; margin-top: 32px; }
  h3 { margin-top: 24px; }
  code { background: #f0f0f0; padding: 2px 6px; border-radius: 3px; font-size: 0.9em; }
  pre { background: #f6f8fa; padding: 16px; border-radius: 6px; overflow-x: auto; }
  pre code { background: none; padding: 0; }
  ul { padding-left: 24px; margin: 8px 0; }
  ol { padding-left: 24px; margin: 8px 0; }
  li { margin-bottom: 6px; }
  a { color: #0366d6; }
  p { margin: 4px 0; }
  hr { border: none; border-top: 1px solid #e1e4e8; margin: 32px 0; }
  table { border-collapse: collapse; width: 100%; margin: 16px 0; }
  th { background: #f6f8fa; padding: 8px 12px; border: 1px solid #e1e4e8; text-align: left; font-weight: 600; }
  td { padding: 8px 12px; border: 1px solid #e1e4e8; }
  tr:nth-child(even) td { background: #f9f9f9; }
'''

theme = DARK if '--dark' in sys.argv else LIGHT

def inline(t):
    t = re.sub(r'\x60([^\x60]+)\x60', r'<code>\1</code>', t)
    t = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href=\"\2\">\1</a>', t)
    t = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'(?<![\"=])https?://[^\s<>)]+', lambda m: f'<a href=\"{m.group()}\">{m.group()}</a>', t)
    return t

def flush_tbl(rows, sep):
    out = ['<table>']
    started_body = False
    for i, row in enumerate(rows):
        if i == sep: continue
        cells = [c.strip() for c in row.strip().strip('|').split('|')]
        if sep >= 0 and i < sep:
            out.append('<thead><tr>' + ''.join(f'<th>{inline(c)}</th>' for c in cells) + '</tr></thead>')
        else:
            if not started_body: out.append('<tbody>'); started_body = True
            out.append('<tr>' + ''.join(f'<td>{inline(c)}</td>' for c in cells) + '</tr>')
    if started_body: out.append('</tbody>')
    out.append('</table>')
    return out

lines = content.split('\n')
h, in_ul, in_ol, in_code, code_buf, in_tbl, tbl_rows, tbl_sep = [], False, False, False, [], False, [], -1
for line in lines:
    s = line.strip()
    if s.startswith('\x60\x60\x60'):
        if in_code:
            h.append('<pre><code>' + '\n'.join(code_buf) + '</code></pre>')
            code_buf = []; in_code = False
        else:
            if in_ul: h.append('</ul>'); in_ul = False
            if in_ol: h.append('</ol>'); in_ol = False
            in_code = True
        continue
    if in_code:
        code_buf.append(html_mod.escape(line)); continue
    if s.startswith('|') and '|' in s[1:]:
        if in_ul: h.append('</ul>'); in_ul = False
        if in_ol: h.append('</ol>'); in_ol = False
        if not in_tbl: in_tbl = True; tbl_rows = []; tbl_sep = -1
        if all(re.match(r'^[-:]+$', c.strip()) for c in s.strip().strip('|').split('|') if c.strip()):
            tbl_sep = len(tbl_rows)
        tbl_rows.append(s)
        continue
    if in_tbl:
        h.extend(flush_tbl(tbl_rows, tbl_sep)); in_tbl = False
    if not s:
        if in_ul: h.append('</ul>'); in_ul = False
        if in_ol: h.append('</ol>'); in_ol = False
        h.append('<br>'); continue
    if s == '---':
        if in_ul: h.append('</ul>'); in_ul = False
        if in_ol: h.append('</ol>'); in_ol = False
        h.append('<hr>'); continue
    m = re.match(r'^(#{1,4})\s+(.*)', s)
    if m:
        if in_ul: h.append('</ul>'); in_ul = False
        if in_ol: h.append('</ol>'); in_ol = False
        n = len(m.group(1))
        h.append(f'<h{n}>{inline(m.group(2))}</h{n}>'); continue
    m = re.match(r'^(\d+)\.\s+(.*)', s)
    if m:
        if in_ul: h.append('</ul>'); in_ul = False
        if not in_ol: h.append('<ol>'); in_ol = True
        h.append(f'<li>{inline(m.group(2))}</li>'); continue
    m = re.match(r'^[-*]\s+(.*)', s)
    if m:
        if in_ol: h.append('</ol>'); in_ol = False
        if not in_ul: h.append('<ul>'); in_ul = True
        h.append(f'<li>{inline(m.group(1))}</li>'); continue
    if in_ul: h.append('</ul>'); in_ul = False
    if in_ol: h.append('</ol>'); in_ol = False
    h.append(f'<p>{inline(s)}</p>')
if in_ul: h.append('</ul>')
if in_ol: h.append('</ol>')
if in_tbl: h.extend(flush_tbl(tbl_rows, tbl_sep))

page = f'<!DOCTYPE html><html><head><meta charset=\"utf-8\"><style>{theme}</style></head><body>{chr(10).join(h)}</body></html>'
with open(out_path, 'w') as f:
    f.write(page)
print(f'OK {out_name}')
" /path/to/file.md --dark
```

The script prints the output filename so you can use it in the browser URL.

### Defaults

- **Default to dark mode** (`--dark`). Only use light mode if the user explicitly asks for light mode.
- Use `open-split` with a direction matching the user's request (right, down, etc.). Default to `open-split` (which splits below).
- **When you modify the source markdown**, always regenerate the same HTML file and `cmux browser <surface> reload`. Never create a second HTML file.
- Reuse the same HTTP server port (18923) across previews. Before starting a new server, check: `lsof -ti:18923`. If already running, skip.

## Safety Rules

- **Never `cmux send` to surfaces you don't own** — the user may be typing in them
- **Always target surfaces you created** with `--surface <ref>`
- **Don't use focus/select commands** (`select-workspace`, `focus-pane`, etc.) unless the user explicitly asked — don't steal focus
- **Clean up when done** — close surfaces and workspaces you created
- **Use `identify --json` first** to understand your current context before creating new terminals
