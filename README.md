# Thread Hiker

A walk inside *Passages* — a third-person exploration of the fiber art of
[Steve Medwin](https://www.medwinfiberart.com), whose free-standing digital
embroidery invites viewers to navigate, not just observe. Here you literally
do: a tiny hiker walks the actual cords of *Passages Series* (2026), crossing
between threads where they touch, the way the artist's own miniature figures do.

**Play it:** [techrabbi.org/thread-hiker](https://techrabbi.org/thread-hiker/)

## Controls

|            | Keyboard | Touch |
|------------|----------|-------|
| Walk       | W / S    | d-pad ▲ ▼ |
| Turn       | A / D    | d-pad ◀ ▶ |
| Map        | M        | map button |

You can't fall off a thread — walk toward a touching or nearby thread to
step across onto it.

## How it's made

- The course is traced from the artist's own vector drawing of the piece
  (`Passages-shapes-2.svg`, stroked centerlines per thread).
  `convert_svg2.py` flattens the curves into `paths.json`; the game builds
  the 3D world from that. Any piece traced this way becomes a walkable world.
- Single-file three.js app (`index.html`): free movement constrained to the
  thread network, procedurally generated twisted-cord texture, tilt-shift
  depth of field for the macro-photograph feel.

Run locally with any static server, e.g. `python3 -m http.server` in this
directory.

## Credits

- Fiber art: **Steve Medwin** — [medwinfiberart.com](https://www.medwinfiberart.com)
- Game: Dan Medwin, built in partnership with Claude
