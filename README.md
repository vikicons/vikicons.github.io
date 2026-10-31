# Vikicons Website

Corporate website for Vikicons, built with [Astro](https://astro.build) and deployed to GitHub Pages at <https://vikicons.github.io>.

The News section is updated automatically from the Construction RSS feeds of [baoxaydung.vn](https://baoxaydung.vn) using GitHub Actions.

## Project Structure

```text
/
├── .github/workflows/
│   ├── deploy.yml            # Builds the Astro site and deploys to GitHub Pages
│   └── update_news.yml       # Fetches RSS news, commits JSON, then triggers deploy
├── public/                   # Static assets (images, icons, etc.)
├── scripts/
│   ├── update_news.py        # Writes src/data/latest_news.json (home page news)
│   └── update_all_news.py    # Writes src/data/all_news.json (News page + categories)
├── src/
│   ├── data/
│   │   ├── latest_news.json  # Latest articles shown on the home page
│   │   └── all_news.json     # All articles shown on the News page
│   ├── layouts/
│   │   └── layout.astro      # Shared page layout
│   ├── pages/                # One file per route
│   │   ├── index.astro       # Home
│   │   ├── about.astro
│   │   ├── services.astro
│   │   ├── projects.astro
│   │   ├── capabilities.astro
│   │   ├── news.astro
│   │   ├── bao-gia.astro
│   │   ├── careers-vn.astro
│   │   ├── contact.astro
│   │   └── 404.astro
│   └── styles/
│       └── global.css
├── astro.config.mjs
├── package.json
└── tsconfig.json
```

## Commands

Run all commands from the project root.

| Command           | Action                                   |
| :---------------- | :--------------------------------------- |
| `npm install`     | Install dependencies                     |
| `npm run dev`     | Start the dev server at `localhost:4321` |
| `npm run build`   | Build the production site to `./dist/`   |
| `npm run preview` | Preview the production build locally     |

## Automatic News Updates

The site is static, so news data is baked into the HTML at build time. The workflow `update_news.yml` keeps it fresh:

1. Runs on a schedule at **22:00 and 10:00 UTC** (05:00 and 17:00 Vietnam time), or manually from the **Actions** tab (**Run workflow**).
2. Runs `scripts/update_news.py`, which reads the main Construction RSS feed and writes the latest articles to `src/data/latest_news.json`.
3. Runs `scripts/update_all_news.py`, which reads the main feed and each sub-category feed and writes `src/data/all_news.json`.
4. Commits the JSON files to `main` only if they changed.
5. Calls `deploy.yml`, which rebuilds and redeploys the site.

### News categories

Articles in `all_news.json` use these category codes. The News page filters tabs by them, so keep the codes in sync with `src/pages/news.astro`.

| Code                    | RSS source                 |
| :---------------------- | :------------------------- |
| `executive-direction`   | `chi-dao-dieu-hanh.rss`    |
| `architecture-planning` | `quy-hoach-kien-truc.rss`  |
| `building-materials`    | `vat-lieu-xay-dung.rss`    |
| `quality-inspection`    | `giam-dinh-chat-luong.rss` |
| `urban-management`      | `quan-ly-do-thi.rss`       |
| `construction-news`     | `xay-dung.rss` (general)   |

Sub-category feeds are read before the general feed, so an article that appears in several feeds keeps its most specific category.

### Run the news scripts locally

```sh
pip install feedparser beautifulsoup4
python scripts/update_news.py
python scripts/update_all_news.py
```

## Deployment

- Pushing to `main` triggers `deploy.yml`.
- In the repository, **Settings → Pages → Source** must be set to **GitHub Actions**.
- The news workflow needs permission to push. It declares `permissions: contents: write`. If the organization restricts workflow permissions, enable **Read and write permissions** under **Settings → Actions → General**.

## Troubleshooting

- **News not updating:** open the latest run of "Auto Update News from Baoxaydung RSS" in the Actions tab and check each step. The `Update all news` log prints how many articles each feed returned.
- **Push rejected locally** (`fetch first`): the bot has pushed new JSON. Run `git pull --rebase origin main`, then push again.
- **Empty news after deploy:** confirm `src/data/*.json` on `main` contains articles. `deploy.yml` checks out `main` so it builds with the latest data.
