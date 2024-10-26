from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests
from bs4 import BeautifulSoup

def get_review_content(url):
    # First try with requests and BeautifulSoup as it's faster
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
    }
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Get title
        title = soup.find('h1').text.strip() if soup.find('h1') else "Title not found"
        
        # Get all paragraphs from the article
        paragraphs = soup.select('div[data-testid="story-content"] p, article p')
        content = '\n\n'.join([p.text.strip() for p in paragraphs if p.text.strip()])
        
        if not content:
            # If no content found, try with Selenium
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
        time.sleep(5)  # Wait for content to load
        
        # Get the title
        title = driver.find_element(By.TAG_NAME, 'h1').text
        
        # Get the review content
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "article")))
        
        # Try different selectors to find the content
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

# Example usage

url = 'https://www.nytimes.com/2024/10/24/movies/venom-the-last-dance-review.html#:~:text=The%20mechanics%20of%20the%20Marvel,over%20a%20Maroon%205%20ballad'
# Try to get the content
result = get_review_content(url)

# Print the results
print("Title:", result['title'])
print("\nContent:")
print(result['content'])