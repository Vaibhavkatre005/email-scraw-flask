from flask import Flask, request, jsonify
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import scrapy
import re
import json
import os

app = Flask(__name__)

# Regular expression for emails
EMAIL_REGEX = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'

class EmailSpider(scrapy.Spider):
    name = 'email_spider'

    def __init__(self, url=None, *args, **kwargs):
        super(EmailSpider, self).__init__(*args, **kwargs)
        self.start_urls = [url] if url else []

    def parse(self, response):
        # Extract all text content from the page
        page_text = response.xpath('//body//text()').getall()
        full_text = ' '.join(page_text)

        # Find all unique email addresses
        emails = list(set(re.findall(EMAIL_REGEX, full_text)))

        # Save emails to a JSON file
        result = {'url': response.url, 'emails': emails}
        output_file = 'emails.json'
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=4)

        self.log(f'Emails extracted and saved to {output_file}')

@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.get_json()
    url = data.get('url')

    if not url:
        return jsonify({'error': 'URL is required'}), 400

    # Create a Scrapy CrawlerProcess
    process = CrawlerProcess(get_project_settings())

    # Run the spider
    process.crawl(EmailSpider, url=url)
    process.start()  # Blocks until the spider finishes

    # Read the result from the JSON file
    if os.path.exists('emails.json'):
        with open('emails.json', 'r') as f:
            result = json.load(f)
        os.remove('emails.json')  # Clean up the file
        return jsonify(result), 200
    else:
        return jsonify({'error': 'Failed to scrape emails'}), 500

if __name__ == '__main__':
    app.run(debug=True)
