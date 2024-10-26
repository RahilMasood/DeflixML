from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import requests
from bs4 import BeautifulSoup
import urllib.parse

def get_nytimes_movie_review_url(movie_name):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        search_query = f"site:nytimes.com {movie_name} movie review"
        google_url = f"https://www.google.com/search?q={urllib.parse.quote(search_query)}"
        
        driver.get(google_url)
        time.sleep(3)
        
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
        
        try:
            nytimes_search = f"https://www.nytimes.com/search?query={urllib.parse.quote(movie_name)}+movie+review"
            driver.get(nytimes_search)
            time.sleep(3)
            
            articles = driver.find_elements(By.CSS_SELECTOR, 'article')
            for article in articles:
                try:
                    link = article.find_element(By.TAG_NAME, 'a')
                    url = link.get_attribute('href')
                    if 'movies' in url and 'review' in url.lower():
                        return url
                except:
                    continue
        except:
            pass
        
        return None
        
    except Exception as e:
        return None
        
    finally:
        driver.quit()

def get_review_content(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,/;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
    }
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        title = soup.find('h1').text.strip() if soup.find('h1') else "Title not found"
        
        paragraphs = soup.select('div[data-testid="story-content"] p, article p')
        content = '\n\n'.join([p.text.strip() for p in paragraphs if p.text.strip()])
        
        if not content:
            return get_review_content_selenium(url)
            
        return {
            'title': title,
            'content': content
        }
        
    except Exception as e:
        print(f"Error with BeautifulSoup approach: {e}")
        return get_review_content_selenium(url)

def get_review_content_selenium(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        driver.get(url)
        time.sleep(5)
        
        title = driver.find_element(By.TAG_NAME, 'h1').text
        
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "article")))
        
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
        print(f"Error with Selenium approach: {e}")
        return {'title': "Error", 'content': f"Failed to extract content: {str(e)}"}
        
    finally:
        driver.quit()

def main():
    movie_name = input("Enter the movie name: ")
    url = get_nytimes_movie_review_url(movie_name)
    
    if url:
        print(f"\nFound review URL: {url}\n")
        result = get_review_content(url)
        print("Title:", result['title'])
        print("\nContent:")
        print(result['content'])
    else:
        print("No review URL found")

if __name__ == "__main__":
    main()
