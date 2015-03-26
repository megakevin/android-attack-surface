android-attack-surface
======================

My capstone project

- android-callgraph: python tool to generate the call graph of android apps.
- googleplay-scraper: Scrapes the google play store and downloads apps' apks and data.
- capstone: LaTeX project with the final paper.

### How to run the google play store scraper

```bash
cd googleplay-scraper
scrapy crawl googleplay
```

### How to run the reviews scraper

```bash
cd googleplay-scraper/reviews
python3 get_reviews.py -app <APK NAME> -n <NUMBER OF REVIEWS TO DOWNLOAD>
```