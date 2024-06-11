import os
import json
import datetime
import psycopg2
from apify_client import ApifyClient

class MyCrawler:
    def __init__(self):
        self.config = self.read_config()
        self.client = ApifyClient(token=self.config['apify']['api_token'])
        self.db_params = {
            'host': 'localhost',
            'port': '5433',
            'database': 'postgres',
            'user': 'postgres',
            'password': 'postgres'
        }

    def read_config(self):
        config_path = os.path.join(os.getcwd(), 'config', 'crawler.json')
        with open(config_path, 'r', encoding='utf-8') as file:
            return json.load(file)

    def run_crawler(self):
        actor_input = {
            'startUrls': self.config['startUrls'],
            'pseudoUrls': self.config['apify']['pseudo_urls'],
            'requestTimeoutSecs': self.config['requestTimeoutSecs'],
            'maxCrawlPages': self.config['maxCrawlPages'],
        }

        run = self.client.actor('apify/website-content-crawler').call(run_input=actor_input)

        print('Crawler run finished.')

        # Fetch actor results from the run's dataset
        results = []
        for item in self.client.dataset(run['defaultDatasetId']).iterate_items():
            results.append(item)

        # Save results to a JSON file with a timestamp in the filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        output_dir = os.path.join(os.getcwd(), 'files')
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        output_file = os.path.join(output_dir, f'results_{timestamp}.json')
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=4)
        print(f'Results saved to {output_file}')

        # Save results to PostgreSQL database
        self.save_to_postgres(output_file)

    def save_to_postgres(self, file_path):
        # Open the file and read its content
        with open(file_path, 'r') as file:
            content = file.read()

        # Establish a connection to the PostgreSQL database
        conn = psycopg2.connect(**self.db_params)

        # Create a cursor object
        cursor = conn.cursor()

        try:
            # Insert file content into the database
            cursor.execute("INSERT INTO files (file_content) VALUES (%s)", (content,))
            conn.commit()
            print("File saved to PostgreSQL database successfully!")
        except psycopg2.Error as e:
            print("Error saving file to PostgreSQL database:", e)
            conn.rollback()
        finally:
            # Close cursor and connection
            cursor.close()
            conn.close()

        # Validate how to make the data available to another service
        # Research Apify documentation or contact Apify support for information on storing data in an external database
        # If Apify supports making data available to another service, determine the appropriate method to accomplish this

if __name__ == "__main__":
    crawler = MyCrawler()
    crawler.run_crawler()
