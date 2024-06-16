import datetime
import re
import requests
from bs4 import BeautifulSoup
from apify_client import ApifyClient
import psycopg2
from apify import Actor

class CrawlerDaCoruna:
    def __init__(self, config):
        self.config = config
        self.client = ApifyClient(token=self.config['apify']['api_token'])

    def extract_title(self, markdown_content):
        match = re.search(r'::(.*?)\[(.*?)\]', markdown_content, re.DOTALL)
        return match.group(2).strip() if match else ""

    def extract_description(self, markdown_content):
        match = re.search(r'::(.*?)\[(.*?)\]', markdown_content, re.DOTALL)
        description = match.group(1).strip() if match else ""

        if description.startswith("Ficha Nova\n\n##"):
            description = description[len("Ficha Nova\n\n##"):]
        elif description.startswith("Ficha Nova\n\n"):
            description = description[len("Ficha Nova\n\n"):]

        description = description.replace("\n\n", ". ").replace("\n", ". ")
        description = description.strip()
        return description

    def extract_date_and_time(self, loaded_time):
        loaded_time_parts = loaded_time.split("T")
        return loaded_time_parts[0], loaded_time_parts[1].replace("Z", "")

    def extract_publication_date(self, url):
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            publication_date_elem = soup.find(class_=self.config['apify']['publication_date_class'])
            if publication_date_elem:
                publication_date = publication_date_elem.get_text().strip()
                return self.transform_publication_date(publication_date)
        return None

    def transform_publication_date(self, date_str):
        months = {
            "Xaneiro": "01",
            "Febreiro": "02",
            "Marzo": "03",
            "Abril": "04",
            "Maio": "05",
            "Xuño": "06",
            "Xullo": "07",
            "Agosto": "08",
            "Setembro": "09",
            "Outubro": "10",
            "Novembro": "11",
            "Decembro": "12"
        }
        day, month, year = re.search(r"(\d{2}) de (.*?) de (\d{4})", date_str).groups()
        month = months[month]
        return f"{year}-{month}-{day}"

    def extract_category(self, url):
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            category = ", ".join([a.get_text().strip() for a in soup.select(self.config['apify']['category_selector'])])
            return category
        return ""

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

                # Add logic for videos if needed
                # for video_tag in content.find_all('video'):
                #     video_link = video_tag['src']
                #     video_title = video_tag.get('alt', '')
                #     video_description = ""  # Add description extraction logic if needed
                #     images_and_videos.append({
                #         "link": video_link,
                #         "title": video_title,
                #         "description": video_description
                #     })

            return images_and_videos
        return []

    def run_crawler(self):
        Actor.log.info('Starting the crawler...')
        actor_input = {
            'startUrls': self.config['startUrls'],
            'includeUrlGlobs': self.config['includeUrlGlobs'],
            'excludeUrlGlobs': self.config['excludeUrlGlobs'],
            'requestTimeoutSecs': self.config['requestTimeoutSecs'],
            'maxCrawlPages': self.config['maxCrawlPages']
        }

        run = self.client.actor('apify/website-content-crawler').call(run_input=actor_input)
        Actor.log.info('Crawler run finished.')

        results = [item for item in self.client.dataset(run['defaultDatasetId']).iterate_items()]

        processed_results = []
        for result in results:
            website_data = {
                'link': result.get('url', ""),
                'title': self.extract_title(result.get('markdown', "")),
                'description': self.extract_description(result.get('markdown', "")),
                'crawl': {}
            }
            if 'crawl' in result:
                loaded_time = result['crawl'].get('loadedTime', "")
                website_data['crawl']['crawler_execution_date'], website_data['crawl']['crawler_execution_time'] = self.extract_date_and_time(loaded_time)

            article_link = website_data['link']
            publication_date = self.extract_publication_date(article_link)

            yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
            if publication_date != yesterday.strftime("%Y-%m-%d"):
                continue

            category = self.extract_category(article_link)
            images_and_videos = self.extract_images_and_videos(article_link)

            article = {
                'link': article_link,
                'description': website_data['description'],
                'publication_date': publication_date,
                'category': category,
                'images_and_videos': images_and_videos
            }

            processed_result = {
                'website_data': website_data,
                'article': article
            }

            processed_results.append(processed_result)

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

        for result in results:
            website_data = result['website_data']
            article = result['article']

            cursor.execute("""
                WITH website_article AS (
                    INSERT INTO website_articles (link, title, description, publication_date, category, crawler_execution_date, crawler_execution_time)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                )
                INSERT INTO media (website_article_id, link, description)
                SELECT website_article.id, %s, %s
                FROM website_article;
            """, (
                website_data['link'],
                website_data['title'],
                website_data['description'],
                article['publication_date'],
                article['category'],
                website_data['crawl']['crawler_execution_date'],
                website_data['crawl']['crawler_execution_time'],
                article['images_and_videos'][0]['link'] if article['images_and_videos'] else None,
                article['images_and_videos'][0]['description'] if article['images_and_videos'] else None
            ))

            for media in article['images_and_videos'][1:]:
                cursor.execute("""
                    INSERT INTO media (website_article_id, link, description)
                    SELECT id, %s, %s
                    FROM website_articles
                    WHERE link = %s;
                """, (
                    media['link'],
                    media['description'],
                    website_data['link']
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

