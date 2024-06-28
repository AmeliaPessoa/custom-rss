from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from apify import Actor
import datetime
import re
import psycopg2
import requests
from bs4 import BeautifulSoup

class CrawlerDaCoruna:
    def __init__(self, config):
        self.config = config
        self.driver = self.init_driver()

    def init_driver(self):
        chrome_options = ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        return webdriver.Chrome(options=chrome_options)

    def extract_title_and_description(self):
        response = requests.get(self.config['startUrls'][0]['url'])
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            title = soup.title.string
            description = soup.find("meta", attrs={"name": "description"})["content"]
            return title, description
        return None, None

    def extract_date_and_time(self, loaded_time):
        return datetime.datetime.strptime(loaded_time, "%Y-%m-%dT%H:%M:%S")

    def transform_publication_date(self, date_str, include_year=True):
        months = {
            "xaneiro": "01", "febreiro": "02", "marzo": "03", "abril": "04",
            "maio": "05", "xuño": "06", "xullo": "07", "agosto": "08",
            "setembro": "09", "outubro": "10", "novembro": "11", "decembro": "12"
        }
        if include_year:
            match = re.search(r"(\d{2}) de (.*?) de (\d{4})", date_str)
            if match:
                day, month, year = match.groups()
                month = months[month.lower()]
                return f"{year}-{month}-{day}"
        else:
            match = re.search(r"(\d{2}) de (.*?)$", date_str)
            if match:
                day, month = match.groups()
                month = months[month.lower()]
                year = datetime.datetime.now().year
                return f"{year}-{month}-{day}"
        return None

    def extract_articles(self):
        articles = []
        page_number = 1
        yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")

        while True:
            response = requests.get(f"{self.config['startUrls'][0]['url']}&ccm_paging_p={page_number}")
            if response.status_code != 200:
                break
            soup = BeautifulSoup(response.text, "html.parser")
            article_elements = soup.select(".c-new--item.u-flex")

            for article_elem in article_elements:
                try:
                    date_elem = article_elem.select_one(".c-new--item__date").text.strip()
                    publication_date = self.transform_publication_date(date_elem, include_year=False)

                    if publication_date < yesterday:
                        return articles

                    if publication_date == yesterday:
                        article_link = article_elem.find("a")["href"]
                        articles.append(self.extract_article_details(article_link))
                except Exception as e:
                    Actor.log.exception(f"Error processing article element: {e}")

            page_number += 1

    def extract_article_details(self, url):
        full_url = self.config['apify']['base_url'] + url
        response = requests.get(full_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            title = soup.select_one(".c-article__detail_title").text.strip()
            publication_date_elem = soup.select_one(".c-article__detail_date")
            publication_date = publication_date_elem["datetime"] if publication_date_elem else None
            description = soup.select_one(".c-article__detail_summary").text.strip()
            categories = ", ".join([cat.text for cat in soup.select(".c-article__left span a")])
            images_and_videos = self.extract_images_and_videos(full_url)
            inserted_at = datetime.datetime.now()

            return {
                'link': full_url,
                'title': title,
                'publication_date': publication_date,
                'author': None,
                'description': description,
                'categories': categories,
                'images_and_videos': images_and_videos,
                'inserted_at': inserted_at
            }
        return {}

    def extract_images_and_videos(self, url):
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            content = soup.find(class_=self.config['apify']['image_container_class'])
            images_and_videos = []

            if content:
                previous_links = set()
                for img_tag in content.find_all('img'):
                    img_link = self.config['apify']['base_url'] + img_tag['src']
                    img_title = img_tag.get('alt', '')
                    img_description = ""
                    footer_image_elem = content.find(class_=self.config['apify']['image_footer_class'])
                    if footer_image_elem:
                        img_description = footer_image_elem.get_text().strip()

                    img_link_common = img_link.rsplit('_', 1)[-1]

                    if img_link_common not in previous_links:
                        images_and_videos.append({
                            "link": img_link,
                            "title": img_title,
                            "description": img_description
                        })

                        previous_links.add(img_link_common)

            return images_and_videos
        return []

    def run_crawler(self):
        Actor.log.info('Starting the crawler...')
        title, description = self.extract_title_and_description()
        inserted_at = datetime.datetime.now()

        website_data = {
            'link': self.config['startUrls'][0]['url'],
            'title': title,
            'description': description,
            'inserted_at': inserted_at
        }

        articles = self.extract_articles()

        processed_results = [{
            'website_data': website_data,
            'article': article
        } for article in articles]

        Actor.log.info(f'Processed {len(processed_results)} results.')
        self.insert_results_to_postgresql(processed_results)

    def insert_results_to_postgresql(self, results):
        Actor.log.info('Connecting to PostgreSQL...')
        conn = psycopg2.connect(
            host=self.config['postgres']['host'],
            port=self.config['postgres']['port'],
            user=self.config['postgres']['user'],
            password=self.config['postgres']['password'],
            database=self.config['postgres']['database']
        )
        cursor = conn.cursor()
        Actor.log.info('Connected to PostgreSQL.')

        website_data = results[0]['website_data']
        cursor.execute("""
            INSERT INTO website (link, title, description, inserted_at)
            VALUES (%s, %s, %s, %s)
            RETURNING id;
        """, (
            website_data['link'],
            website_data['title'],
            website_data['description'],
            website_data['inserted_at']
        ))

        website_id = cursor.fetchone()[0]

        for result in results:
            article = result['article']
            cursor.execute("""
                WITH article_insert AS (
                    INSERT INTO articles (website_id, link, title, publication_date, author, description, categories, inserted_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                )
                INSERT INTO media (article_id, link, title, description)
                SELECT id, %s, %s, %s FROM article_insert;
            """, (
                website_id,
                article['link'],
                article['title'],
                article['publication_date'],
                article['author'],
                article['description'],
                article['categories'],
                article['inserted_at'],
                article['images_and_videos'][0]['link'] if article['images_and_videos'] else None,
                article['images_and_videos'][0]['title'] if article['images_and_videos'] else None,
                article['images_and_videos'][0]['description'] if article['images_and_videos'] else None
            ))

            for media in article['images_and_videos'][1:]:
                cursor.execute("""
                    INSERT INTO media (article_id, link, title, description)
                    SELECT id, %s, %s, %s
                    FROM articles
                    WHERE link = %s;
                """, (
                    media['link'],
                    media['title'],
                    media['description'],
                    article['link']
                ))

        conn.commit()
        cursor.close()
        conn.close()
        Actor.log.info('Data inserted into PostgreSQL database.')

async def main():
    async with Actor:
        Actor.log.info('CrawlerDaCoruna started.')

        config = await Actor.get_input()
        crawler = CrawlerDaCoruna(config)
        crawler.run_crawler()

        Actor.log.info('CrawlerDaCoruna finished.')

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
