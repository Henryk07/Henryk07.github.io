# cv.henrykchan.com

Personal homepage of Henryk Chan (Haolin Chen). Plain Jekyll, no theme, served by GitHub Pages.

The page has two sides, switched with the control at the top:

- **Academic**: about, news, publications, research, education, honours
- **Life & developer**: projects, activities, and Buy me a coffee

`/professional/` is a separate, recruiter-facing page (experience, skills, awards), linked from the top bar.

## Updating content

Almost everything lives in `_data/`. Edit the YAML and push; you shouldn't need to touch HTML.

| File | What's in it |
| --- | --- |
| `_data/profile.yml` | Name, taglines, links for each side, Buy me a coffee URL |
| `_data/academic.yml` | News, publications, research, education, honours |
| `_data/life.yml` | Projects and activities |
| `_data/professional.yml` | Everything on `/professional/` |

The two intro paragraphs are in `_includes/academic.html` and `_includes/life.html`.

## Citations

`.github/workflows/scholar.yml` runs every Monday (or on demand from the Actions tab). It:

1. fetches Google Scholar data and pushes it to the `google-scholar-stats` branch, which the page reads live;
2. writes the new counts into `_data/academic.yml` and `_data/profile.yml` and commits them if they changed,
   so the numbers in the HTML are right even before JavaScript runs.

It needs a repository secret `GOOGLE_SCHOLAR_ID` (`Yu9lHQgAAAAJ`). To add a paper's live count, put its
Scholar id (the part after `citation_for_view=` in its Scholar link) in `scholar_id`.

## Local preview

```sh
bundle config set --local path vendor/bundle
bundle install
bundle exec jekyll serve --livereload
```
