# inbox

Drop ONE zip here (Add file → Upload files) and the `inbox` workflow
(`.github/workflows/inbox.yml`) unpacks it: every file goes to the path it
carries inside the zip, the zip is removed, and it all lands as one commit.

- Paths inside the zip are relative to the repo root (`player/sound.js`,
  `dracula/sound/fire.mp3`).
- A zip made by right-clicking a folder in Finder is fine — the wrapper
  folder is stripped, and `__MACOSX` / `.DS_Store` are ignored.
- It refuses — and changes nothing — if any path is absolute, contains `..`,
  or points into `.github/` or `inbox/`.
- Watch it run under the **Actions** tab. The log lists every file placed.

This README keeps the folder alive between deliveries; leave it here.
