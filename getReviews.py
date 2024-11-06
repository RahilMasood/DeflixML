from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from textblob import TextBlob
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize
import urllib.parse
import numpy as np
import re

def get_nytimes_movie_review_url(movie_name):
    chrome_options = Options()
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        search_query = f"site:nytimes.com {movie_name} movie review"
        google_url = f"https://www.google.com/search?q={urllib.parse.quote(search_query)}"
        
        driver.get(google_url)
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.g')))
        
        results = driver.find_elements(By.CSS_SELECTOR, 'div.g')
        
        for result in results:
            try:
                link = result.find_element(By.CSS_SELECTOR, 'a')
                url = link.get_attribute('href')
                title = result.find_element(By.CSS_SELECTOR, 'h3').text.lower()
                
                if ('nytimes.com' in url and 
                    'movies' in url and 
                    ('review' in title or 'review' in url.lower())):
                    return url
            except:
                continue

        # Backup NYTimes search
        nytimes_search = f"https://www.nytimes.com/search?query={urllib.parse.quote(movie_name)}+movie+review"
        driver.get(nytimes_search)
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'article')))
        
        articles = driver.find_elements(By.CSS_SELECTOR, 'article')
        for article in articles:
            try:
                link = article.find_element(By.TAG_NAME, 'a')
                url = link.get_attribute('href')
                if 'movies' in url and 'review' in url.lower():
                    return url
            except:
                continue
        
        return None
    
    finally:
        driver.quit()

def get_review_content(url):
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'h1')))
        
        try:
            accept_cookies = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accept')]"))
            )
            accept_cookies.click()
        except:
            pass

        title = driver.find_element(By.TAG_NAME, 'h1').text
        
        selectors = [
            'div[data-testid="story-content"] p',
            'article p.css-at9mc1',
            'article p',
            '.StoryBodyCompanionColumn p'
        ]
        
        content = []
        for selector in selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    content = [elem.text for elem in elements if elem.text.strip()]
                    break
            except:
                continue
        
        return {
            'title': title,
            'content': '\n\n'.join(content) if content else "Content not found"
        }
        
    except Exception as e:
        print(f"Error retrieving content: {e}")
        return {'title': "Error", 'content': f"Failed to extract content: {str(e)}"}
        
    finally:
        driver.quit()

def preprocess_text(text):
    text = re.sub(r'\s+', ' ', text)  # Remove extra whitespace
    text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
    return text.lower()

def analyze_sentiment(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    return polarity

def extract_features(text):
    features = ["plot", "acting", "direction", "cinematography", "music"]
    scores = []
    sentences = sent_tokenize(text)
    for feature in features:
        feature_text = ' '.join([sentence for sentence in sentences if feature in sentence.lower()])
        score = analyze_sentiment(feature_text)
        scores.append(score)
    return np.mean(scores)

def generate_rating(review_text):
    clean_text = preprocess_text(review_text)
    sentiment_score = analyze_sentiment(clean_text)
    feature_score = extract_features(clean_text)
    final_rating = (sentiment_score * 0.5 + feature_score * 0.5) * 10
    final_rating = max(0, min(10, round(final_rating, 1)))  # Ensure rating is between 0 and 10
    return final_rating

def main():
    movie_name = input("Enter the movie name: ")
    url = get_nytimes_movie_review_url(movie_name)
    
    if url:
        print(f"\nFound review URL: {url}\n")
        result = get_review_content(url)
        rating = int(generate_rating(result['content']) * 10)
        print(f"Rating for the movie: {rating}/10")
    else:
        print("No review URL found")

if __name__ == "__main__":
    main()
