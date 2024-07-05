
from flask import Flask, jsonify, request,  render_template
import requests
from bs4 import BeautifulSoup
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from collections import defaultdict
from collections import defaultdict, Counter
from concurrent.futures import ThreadPoolExecutor
from flask_cors import CORS
import random

nltk.download('punkt')
nltk.download('stopwords')



app = Flask(__name__)
CORS(app)

def summarize_text(text):
    
    sentences = sent_tokenize(text)

    
    stop_words = set(stopwords.words('english'))
    words = word_tokenize(text.lower())
    words = [word for word in words if word.isalnum() and word not in stop_words]

    
    word_freq = defaultdict(int)
    for word in words:
        word_freq[word] += 1

    
    sentence_scores = defaultdict(int)
    for sentence in sentences:
        for word in word_tokenize(sentence.lower()):
            if word in word_freq:
                sentence_scores[sentence] += word_freq[word]

    # Sort sentences by score and get the top 3 sentences for the summary
    summary_sentences = sorted(sentence_scores, key=sentence_scores.get, reverse=True)[:3]
    summary = ' '.join(summary_sentences)

    top_keywords = Counter(word_freq).most_common(5)
    #print(top_keywords)
    

    return summary, top_keywords

def scrap_wikipedia(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    
    title_tag = soup.find('span', class_="mw-page-title-main")
    title = title_tag.text.strip() if title_tag else ""

    
    div_description = soup.find('div', class_="shortdescription nomobile noexcerpt noprint searchaux")
    description = div_description.text.strip() if div_description else ""

   
    div = soup.find('div', class_="mw-content-ltr mw-parser-output")
    if div is None:
        return title, description, "", None

    
    paragraphs = div.find_all(['p', 'h2'])
    text = ' '.join([para.get_text() for para in paragraphs])

  
    first_img = div.find('img')
    first_fig = div.find('figure')
    img_url = None

    if first_img:
        img_url = first_img.get('src')
        if img_url and not img_url.startswith('http'):
            img_url = 'https:' + img_url
    elif first_fig:
        img_tag = first_fig.find('img')
        if img_tag:
            img_url = img_tag.get('src')
            if img_url and not img_url.startswith('http'):
                img_url = 'https:' + img_url

    return title, description, text, img_url

def get_random_wikipedia_url():
    response = requests.get('https://en.wikipedia.org/wiki/Special:Random')
    return response.url


@app.route('/generate_content', methods=['GET'])
def generate_content():
    page = int(request.args.get('page', 1))  # Default page number is 1
    page_size = int(request.args.get('page_size', 10))  # Default page size is 10

    def fetch_content():
        random_url = get_random_wikipedia_url()
        title, description, main_text, image = scrap_wikipedia(random_url)
        summary, keywords = summarize_text(main_text)
        return {
            'title': title,
            'description': description,
            'summary': summary,
            'keywords': keywords,
            'image': image,
            'url': random_url
        }

    with ThreadPoolExecutor(max_workers=page_size) as executor:
        contents = list(executor.map(lambda _: fetch_content(), range(page_size)))

    return jsonify(contents)

@app.route('/')
def fetch_html():
    page = 1  # Default page number
    page_size = 10  # Default page size

    def fetch_content():
        random_url = get_random_wikipedia_url()
        title, description, main_text, image = scrap_wikipedia(random_url)
        summary, keywords = summarize_text(main_text)
        return {
            'title': title,
            'description': description,
            'summary': summary,
            'keywords': keywords,
            'image': image,
            'url': random_url
        }

    with ThreadPoolExecutor(max_workers=page_size) as executor:
        contents = list(executor.map(lambda _: fetch_content(), range(page_size)))

    return render_template('index.html', contents=contents)

@app.route('/fetch_news', methods=['GET'])
def fetch_news():
    url = "https://www.hindustantimes.com/india-news"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive'
    }

    # Start a session
    with requests.Session() as session:
        # Perform a GET request to establish the session
        session.get(url)

        # Now you can access authenticated pages (assuming cookies are set)
        response = session.get(url, headers=headers)

        # Check if the request to the desired page was successful
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            # Example: Extracting text content from specific elements
            data_holder = soup.find('section', class_="listingPage")
            if data_holder:
                elements = data_holder.find_all('div', class_=lambda x: x and x.startswith('cartHolder'))

                news_list = []
                for element in elements:
                    data_description = element.find('h2', class_='sortDec').text.strip()
                    data_weburl = element.get('data-weburl')
                    data_vars_section = element.get('data-vars-section')
                    data_vars_story_title = element.get('data-vars-story-title')
                    data_vars_story_time = element.get('data-vars-story-time')

                    # Construct each news item as a dictionary
                    news_item = {
                        "web_url": data_weburl,
                        "section": data_vars_section,
                        "story_title": data_vars_story_title,
                        "story_time": data_vars_story_time,
                        "story_description": data_description
                    }
                    news_list.append(news_item)

                return jsonify(news_list)

            else:
                return jsonify({"error": "No data holder found"})

        else:
            return jsonify({"error": f"Failed to retrieve data from {url}, status code: {response.status_code}"})

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
