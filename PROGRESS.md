# Progress

## 2026-11-21: New homepage (replaces the AcadHomepage fork)

- [x] Fresh, non-fork Jekyll site with content in `_data/*.yml`
- [x] Academic / Life & developer switch with hash links (`/#academic`, `/#life`)
- [x] Signal-trace hero (ECG for Academic, bitstream for Life & developer), light and dark themes
- [x] Life & developer side: intro, projects, activities, Buy me a coffee
- [x] Fixed Scholar crawler (pin `bibtexparser<2`, modern actions, manual trigger)
- [x] Scholar workflow runs weekly and writes fresh counts back into `_data` (163 citations as of today)
- [x] Added arXiv YOLOv8 arrhythmia paper (co-first), DOI links, Cambridge Bioelectronics Laboratory
- [x] Imperial research and Hammersmith volunteering end Sep 2025
- [x] Add ISFOE Young Researcher Award 2026, Danaher news, NeuMeC Lab
- [x] Old repo renamed, new repo live at cv.henrykchan.com

## 2026-11-22: Professional page (branch `feat/professional-page`)

- [x] `/professional/` with highlights, experience (Danaher, Cambridge, Imperial, teaching), skills, awards, leadership, education
- [x] Blended ECG-to-bitstream trace, linked from the homepage bar
- [ ] Review on device, then PR and merge
- [ ] Make the Scholar crawler reliable (Google blocks GitHub Actions IPs)
- [x] Review the design in a browser and on a phone
- [x] Rename the old repo to `henryk07.github.io-legacy`
- [x] Create the new `Henryk07.github.io` repo, push, enable Pages with custom domain `cv.henrykchan.com`
- [x] Add the `GOOGLE_SCHOLAR_ID` secret and run the Scholar workflow once (failed: Scholar blocked the runner)
