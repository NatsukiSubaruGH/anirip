AniRip — v0.0.1 (beta1)
Author: Natsuki Subaru
Release date: 12 Aug 2025 (12/08/2025)
License: MIT

please read the full file before downloading
[⬜️ **Download Windows x64 version** ⬜️](https://github.com/NatsukiSubaruGH/anirip/releases/download/v0.0.1/ANIRIP.WINDOWS.x64.version.0.0.1.zip)

TL;DR
AniRip is a small PyQt6 desktop app that finds direct episode sources from AnimePahe and downloads episodes in parallel. On first run it silently downloads and caches UI assets (icon / images / svgs) to a per-user cache folder, logs where it put them, and will exit if any required asset fails to download (per project policy). Use it responsibly.Based on ANIMEPAHE AND ANIMESAM API,you can change this to any other api for your use case

Table of contents
Features & behaviour

Quick start (run / first run)

UI: what everything does (exact behavior matched to the code)

File locations (where assets/logs and downloads live)

Known issues / limitations (what’s intentionally “buggy”)

Troubleshooting (common errors and fixes)

Reporting bugs / contributing

Terms & Conditions (you accept by downloading/using)

Disclaimer & liability 

1 — Features & behaviour (from the code)
GUI built with PyQt6.

Searches AnimePahe via its public API (top 6 results returned).

Fetches episode release data (handles pagination).

Resolves direct sources and groups by quality and language (JP Sub / Eng Dub).

Download worker uses ThreadPoolExecutor (parallel downloads; MAX_WORKERS = 10).

Progress bar reports percent of episodes completed (not byte-by-byte).

First run: downloads assets listed in ASSET_URLS (icon.ico, icon.jpg, github.svg, reddit.svg, help.svg). If any asset fails to download, the app logs the error and exits.

Asset cache/log location: per-user folder (Windows -> %LOCALAPPDATA%\AniRip\assets, other OS -> ~/.anirip/assets).

The UI sets the window icon to icon.ico (if present) and uses icon.jpg as the background.

Downloads saved to a folder named after the anime title (sanitized) in the current working directory: ./<sanitized-title>/....

3 — UI & exact usage (how the code works)
Search

Enter an anime name in the search box and press Search.

App calls se(q) to query AnimePahe and shows up to 6 matches in a combo box.

Select result

Choose the anime from the combo (anime_select).

Language

Choose JP Sub or Eng Dub.

Quality

Choose 1080p, 720p, or 360p. (App filters sources to those matching the quality string.)

Episodes input (supported formats — code parses these forms):

all → download all episodes,

range start-end or start-end → e.g. range 1-12 or 1-12,

list x,y,z or x,y,z → e.g. list 1,3,5 or 1,3,5,

a single number to download just that episode.

Input must be valid and within episode count (app validates against the fetched episode list).

Start Download

Creates output dir sf(title) where sf() sanitizes names, then starts DownloadWorker.

Worker fetches source URLs (via sc() + pr()), selects the requested quality & language, then downloads episodes in parallel using ThreadPoolExecutor.

Progress bar shows percentage of episodes completed; log text shows per-episode status.

Logs

UI log shows runtime messages.

Persistent assets.log in cache folder stores asset download events and errors.

4 — File & cache locations (exact)
Assets cache:

Windows: %LOCALAPPDATA%\AniRip\assets\

Linux/macOS: ~/.anirip/assets/
Files: icon.ico, icon.jpg, github.svg, reddit.svg, help.svg, assets.log.

Downlaoded anime episodes:

Saved in current working directory in a folder sanitized from anime title (example: ./My_Anime_Title - Ep001 - 1080p.mp4).

Log file: assets.log (written to the assets cache), contains timestamps and asset paths or download errors.

8 — Reporting bugs / contributing
Open an issue on GitHub: https://github.com/NatsukiSubaruGH/anirip

Include: exact OS, Python version (if running raw), exe build type, assets.log (if present), and exact reproduction steps.

9 — Terms & Conditions (acceptance by download / use)
By downloading, installing, or using AniRip (the “Software”), you agree to these Terms & Conditions. If you do not agree, do not download, install, or use the Software.

Acceptance. Downloading, installing, or using the Software constitutes acceptance of these Terms.

Use Restrictions. You must not use the Software to infringe copyrights, distribute pirated content, or otherwise break applicable laws. Use is limited to lawful, personal, and educational purposes only.

Right to Disable / Modify. The author (Natsuki Subaru) reserves the unilateral right to modify, disable, suspend, or terminate the Software or access to it at any time and for any reason, without prior notice.

No Guarantees. The Software is provided as-is. The author gives no warranties (express or implied) about performance, fitness for a particular purpose, non-infringement, or uninterrupted operation.

Data & Logs. The Software will download and cache assets and write assets.log in your user folder; by using the Software you consent to this behavior.

Termination. The author retains the right to revoke your permission to use the Software. If revoked, you must stop using and remove the Software.

Governing law / enforcement. These Terms are intended to be legally enforceable, but if any clause is invalid under your jurisdiction, the rest remain effective to the fullest extent permitted by law.

Changes to Terms. The author may change these Terms at any time; continued use after changes indicates acceptance.

10 — Legal Disclaimer & Liability (big — READ CAREFULLY)
Not legal advice: This is boilerplate legal language and not a substitute for professional legal counsel. If you want true legal protection, consult a qualified attorney who can tailor terms to your jurisdiction and risk profile.

No liability: To the maximum extent permitted by law, in no event will the author (Natsuki Subaru), contributors, or distributors be liable for any direct, indirect, incidental, consequential, punitive, or special damages arising from use of or inability to use the Software, including but not limited to loss of profits, data, or goodwill, even if the author was advised of the possibility of such damages.

Indemnification: You agree to indemnify and hold harmless the author from any claims, liabilities, losses, damages, and expenses (including legal fees) arising from your use or misuse of the Software or your violation of these Terms.

Copyright: user responsibility. The Software may be used to access or download media. Downloading or distributing copyrighted content without permission may be illegal in your jurisdiction. You alone are responsible for compliance with law. The author does not condone or encourage copyright infringement.

Severability & survival. If any provision is found invalid, the remaining provisions remain in force. These provisions survive termination of your license.
This program is for educational purposes on the use of pyhton requests and gui to access content
