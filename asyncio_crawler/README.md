# asyncio_crawler
Async crawler for news.ycombinator.com.

- crawl top 30 news from root page with specified interval
- download and save news pages
- download and save pages by links in comments to news
- use:
  - aiohttp
  - beautifulsoup


# requirements
  - Python v3
  
# how to run
```
python3 crawler.py -h
usage: crawler.py [-h] [-o OUTPUT] [-i INTERVAL] [-d] [-r RATE]
```
  
# how to run in Docker 
```
docker-compose up -d --build
```
