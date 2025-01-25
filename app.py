from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# Helper function to scrape webpage content
def scrape_page(url):
    try:
        # Send GET request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise error for invalid status codes

        # Parse HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract common page elements
        title = soup.title.string if soup.title else 'No title found'
        meta_description = ''
        for meta in soup.find_all('meta'):
            if meta.get('name') == 'description':
                meta_description = meta.get('content', 'No description found')
                break
        
        # Extract links and images
        links = [a['href'] for a in soup.find_all('a', href=True)]
        images = [img['src'] for img in soup.find_all('img', src=True)]

        return {
            'title': title,
            'meta_description': meta_description,
            'links': links,
            'images': images
        }

    except requests.exceptions.RequestException as e:
        return {'error': str(e)}

# API endpoint to scrape page
@app.route('/scrape', methods=['POST'])
def scrape():
    # Get URL from request data
    data = request.get_json()
    url = data.get('url')

    if not url:
        return jsonify({'error': 'URL is required'}), 400

    # Scrape page and return the result
    result = scrape_page(url)

    # Return JSON response
    if 'error' in result:
        return jsonify(result), 400
    
    return jsonify(result), 200

if __name__ == '__main__':
    app.run(debug=True)
