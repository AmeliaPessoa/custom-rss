import os
import json
import datetime
from apify_client import ApifyClient

class MyCrawler:
    def __init__(self):
        self.config = self.read_config()
        self.client = ApifyClient(token=self.config['apify']['api_token'])

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
        results = [item for item in self.client.dataset(run['defaultDatasetId']).iterate_items()]

        # Save results to a JSON file with a timestamp in the filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        output_dir = os.path.join(os.getcwd(), 'files')
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        output_file = os.path.join(output_dir, f'results_{timestamp}.json')
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=4)
        print(f'Results saved to {output_file}')

        # Insert results into PostgreSQL database using Apify actor
        self.insert_results_to_postgresql(run['defaultDatasetId'])

    def insert_results_to_postgresql(self, dataset_id):
        # Prepare the input for the postgresql-insert actor
        run_input = {
            "datasetId": dataset_id,
            "data": {
                "connection": {
                    "host": self.config['postgres']['host'],
                    "port": self.config['postgres']['port'],
                    "user": self.config['postgres']['user'],
                    "password": self.config['postgres']['password'],
                    "database": self.config['postgres']['database']
                },
                "table": self.config['postgres']['table']
            }
        }

        # Run the postgresql-insert actor
        self.client.actor('petr_cermak/postgresql-insert').call(run_input=run_input)
        print('Data inserted into PostgreSQL database.')

if __name__ == "__main__":
    crawler = MyCrawler()
    crawler.run_crawler()
