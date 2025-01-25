from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)

# Regular expressions for emails and mobile numbers
EMAIL_REGEX = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
PHONE_REGEX = r'(\+?\d{1,3}[-.\s]?)?(\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}'

# Helper function to scrape webpage content
def scrape_page(url):
    try:
        # Send GET request to the URL
        response = requests.get(url, timeout=10)
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

        # Extract all text for email and phone number extraction
        text = soup.get_text(separator=' ', strip=True)

        # Find all unique email addresses
        emails = list(set(re.findall(EMAIL_REGEX, text)))

        # Find all unique phone numbers
        phone_numbers = list(set(re.findall(PHONE_REGEX, text)))
        # Clean up phone numbers by joining the tuples and removing spaces/dashes
        phone_numbers = [''.join(number).strip() for number in phone_numbers]

        # Optionally, extract additional URLs from scripts or other tags
        # For simplicity, we are using the links extracted above

        return {
            'title': title,
            'meta_description': meta_description,
            'links': links,
            'images': images,
            'emails': emails,
            'phone_numbers': phone_numbers
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
