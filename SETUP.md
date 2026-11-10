# Nayan-Programmer — Naruto-inspired GitHub Profile

This is a personalized, editable profile README inspired by the *layout and animation approach* of the uploaded example, using **your own supplied Naruto-style character artwork**. The exact materials in the example profile, its personal details and its repo statistics have not been reused.

## What's inside

| File | Purpose |
|---|---|
| `README.md` | Main page displayed on your GitHub profile |
| `hero.svg` | Animated EchooAI hero, cycling role text and a 4-second still-frame camera loop |
| `about-life.svg` | Ninja-way browser, training-arc slides and animated rings |
| `stack.svg` | Rotating ninja jutsu stack, orbiting tech-brand marks and glowing chips |
| `id-dashboard.svg` | Ninja registration badge, swinging lanyard and classified-project dashboard |
| `connect.svg` | Pointing character and GitHub / EchooAI / upcoming announcement cards |
| `profile-3d-contrib/profile-night-view.svg` | Clearly labeled placeholder, replaced by actual contributions after workflow runs |
| `.github/workflows/profile-3d.yml` | Daily night-city generation; also manually runnable |
| `profile_config.json` | Your profile settings and future personal details |
| `build_profile.py` | Rebuild the standalone animated SVG files |
| `generate_readme.py` | Rebuild the `README.md` file from your settings |
| `source/` | Original character artwork used by the generator |
| `tools/embed_video.py` | Optional: replace still-frame loop with actual video frames |

## Publish to GitHub in ~five steps

1. On GitHub, create a new **public** repository called `Nayan-Programmer` while logged into the `Nayan-Programmer` account. The complete path must be `Nayan-Programmer/Nayan-Programmer`. It is **only this public profile repository** that needs to be visible; your actual project repositories can remain private.
2. Upload the top-level `README.md`, five SVG files, placeholder image directory and `.github/workflows/profile-3d.yml` at the same relative paths. You may upload the editable scripts and sources too; they are optional for rendering, but useful for future editing.
3. Go to the repository's **Settings → Actions → General** and make sure workflows can get permission to write repository content (or that the included workflow's `contents: write` permission is allowed by your org policies).
4. Open **Actions → GitHub Profile 3D Night City → Run workflow**. It generates the real contribution city and replaces the placeholder SVG. The scheduled workflow runs once a day (03:00 IST).
5. Open `https://github.com/Nayan-Programmer` to view the profile. If GitHub caches an older SVG, change the image's `?v=1` suffix in README to `?v=2`.

**Privacy:** The README and five visual cards do not include private repository names, star counts or proprietary files. GitHub's contributions display can show overall private activity only if you choose to enable *Include private contributions on my profile* in your GitHub settings; it does not reveal private repository names. Scheduled workflows can be delayed by GitHub. The first-run placeholder exists so there is no broken image beforehand.

## Edit the content

Open `profile_config.json`. Edit the `name`, `role`, `github`, `company`, `pitch` and `role_lines` keys. Enter `email` only if you want an email link in README; it is intentionally blank. `skills` and `hobbies` are deliberately not claimed as verified skills or real-world leisure activities. In the card designs, the present technology icons are **example ornamentation**. Replace them with your actual stack in the `groups` in `stack()` of `build_profile.py` before describing them as your expertise.

The artistic copy in `about()`, `id_dashboard()` and `connect()` is intentionally ninja-themed and may be edited directly inside `build_profile.py`. The generator turns text into vector outlines, so editing visible SVG text with find/replace will not work reliably — modify the source and rebuild.

```bash
python -m pip install -r requirements.txt
python build_profile.py
```

The local generator searches for installed **Inter**, **Go Mono** and **Simple Icons** fonts in `FONT_CANDIDATES` at the top of `build_profile.py`. If those fonts are elsewhere on your PC, update their local paths. Font files are not bundled, but all needed glyphs are outlined inside each final SVG, which means profile viewers never need to install the fonts.

You can edit the SVG artwork directly in **Inkscape**, but for permanent text/layout edits, use the Python generator. The generated files require **no network assets** while rendering: artwork is embedded as PNG/JPEG and icons/text are vectors. SVG animation uses SMIL/CSS only (no JavaScript).

## Optional: add your real waving clip

No actual waving video was included in the provided character uploads. `hero.svg` currently contains a genuine **animated still-image loop**, not extracted video footage. To supply your own footage:

```bash
python -m pip install opencv-python
python tools/embed_video.py path/to/your-waving-video.mp4
```

Run the video embed tool **after** `python build_profile.py`, because a full rebuild regenerates the still-image placeholder. For best GitHub load times use a short, cropped, low-resolution clip. The current cards were browser-tested at multiple animation timestamps, and they contain a stable static fallback when animation is blocked.

## Credits

- Character images: supplied by you in the conversation
- Tech icon artwork: Simple Icons vector glyphs (examples, not verified personal skills)
- Night-city generation: [yoshi389111/github-profile-3d-contrib](https://github.com/yoshi389111/github-profile-3d-contrib)
- Naruto-inspired theme is unofficial fan-style artwork, not an affiliation with the franchise
