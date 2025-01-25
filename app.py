from flask import Flask, request, jsonify
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks
from scrapy import signals
from scrapy.signalmanager import dispatcher
import threading
import json

app = Flask(__name__)

# Define a thread-safe way to run Scrapy
class ScrapyThread(threading.Thread):
    def __init__(self, runner, spider_cls, **kwargs):
        threading.Thread.__init__(self)
        self.runner = runner
        self.spider_cls = spider_cls
        self.kwargs = kwargs
        self.items = []

    def run(self):
        dispatcher.connect(self.item_scraped, signal=signals.item_scraped)
        reactor.callFromThread(self.run_spider)

        if not reactor.running:
            reactor.run(installSignalHandlers=False)

    def run_spider(self):
        deferred = self.runner.crawl(self.spider_cls, **self.kwargs)
        deferred.addBoth(lambda _: reactor.stop())

    def item_scraped(self, item):
        self.items.append(item)

@app.route('/scrape', methods=['POST'])
def scrape():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'URL parameter is required'}), 400

    settings = get_project_settings()
    runner = CrawlerRunner(settings)

    # Import your Scrapy spider class here
    from your_project.spiders.your_spider import YourSpider

    # Create and start ScrapyThread
    scrapy_thread = ScrapyThread(runner, YourSpider, start_urls=[url])
    scrapy_thread.start()
    scrapy_thread.join()

    return jsonify(scrapy_thread.items)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
