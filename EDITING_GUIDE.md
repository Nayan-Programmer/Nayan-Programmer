# How to edit your Midnight GitHub Profile

## Quick edit
1. Open the folder in VS Code.
2. Open **profile_config.json**.
3. Replace the dummy name, GitHub username, email, city, company, pitch, skills, hobbies, social URLs and demo repo statistics. Keep valid JSON: use double quotes and commas between fields.
4. Run the generator from this folder:

   ```bash
   python -m pip install pillow fonttools lxml
   python build_profile.py
   ```

5. Open `hero.svg`, `about-life.svg`, `stack.svg`, `id-dashboard.svg`, and `connect.svg` in a browser to preview.
6. Push `README.md`, the five SVG cards, and `.github/workflows/profile-3d.yml` to a **public GitHub profile repository named the same as your GitHub username** (e.g. username/username).
7. In GitHub, open **Actions > GitHub-Profile-3D-Contrib > Run workflow** for the initial 3D contribution image. The workflow then refreshes daily.

## Important: fonts and dependencies
The SVG files are self-contained and **will display without installing fonts**. The generator draws type and Simple Icons as vector outlines instead of shipping font files. *Rebuilding* needs font files installed on the computer generating the SVGs, as well as Pillow, fontTools, and lxml. The script currently searches Linux paths for Inter, Go Mono, and Simple Icons. On Windows or macOS, modify `FONT_CANDIDATES` at the top of `build_profile.py` to point to equivalent local fonts. No font binaries are included in this package.

## Which file changes what?
- **profile_config.json:** personal details, skills/hobbies, public links, manually entered stats, demo repo names
- **build_profile.py:** layouts, gradients/colors, animation timing and placements, art references
- **source/hacker_character.png:** illustrated character in hero and animated pseudo-video
- **source/pointing_character.png:** character in contact panel
- **source/nayan_sticker.png:** illustrated character in ID dashboard / about panel
- **generate_readme.py:** README structure
- **README.md:** markdown text, projects table, image order

## Important limitation about the video
The original message included two still images. No extractable video file is included in this project. The hero currently uses twelve JPEG frames rendered from the still image to approximate a gentle 4-second movement. To use a real waving clip, update `camera_frames()` in `build_profile.py` to load and encode actual frames from your video before rebuilding.

## Changing colors
Find `#0d0e16`, `#22d3ee`, `#a78bfa`, and `#f472b6` in `build_profile.py`, and change the hex values. Then regenerate the SVG files.

## No-code option
Send your real details and requested changes into ChatGPT; ask it to update the SVGs and README from this project. For layout-only manual tweaks, use an SVG editor such as Inkscape. Note that SVG lettering is outlined, not live editable text.

## Preview and GitHub notes
Modern browsers render most CSS and SMIL animations; GitHub may handle unsupported animation differently. Test the published profile itself. The SVG files don't load remote photos or fonts. All the five profile card links include `?v=1` for cache busting.
