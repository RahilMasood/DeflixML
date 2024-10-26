from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import urllib.parse

def get_nytimes_movie_review_url(movie_name):
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    # Initialize the driver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        # Construct the search URL
        search_query = f"site:nytimes.com {movie_name} movie review"
        google_url = f"https://www.google.com/search?q={urllib.parse.quote(search_query)}"
        
        # Navigate to Google
        driver.get(google_url)
        time.sleep(3)
        
        # Find all search results
        results = driver.find_elements(By.CSS_SELECTOR, 'div.g')
        
        # Look through results for NY Times movie review links
        for result in results:
            try:
                link = result.find_element(By.CSS_SELECTOR, 'a')
                url = link.get_attribute('href')
                title = result.find_element(By.CSS_SELECTOR, 'h3').text.lower()
                
                # Check if it's a NY Times URL and looks like a movie review
                if ('nytimes.com' in url and 
                    'movies' in url and 
                    ('review' in title or 'review' in url.lower())):
                    return url  # Return just the URL of the first match
            except:
                continue
        
        # If no results found, try NY Times direct search
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

def main():
    movie_name = input("Enter the movie name: ")
    url = get_nytimes_movie_review_url(movie_name)
    if url:
        print(url)
    else:
        print("No review URL found")

if __name__ == "__main__":
    main()
