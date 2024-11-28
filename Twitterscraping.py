from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
import time
from bs4 import BeautifulSoup

# Function to authenticate and set up the WebDriver
def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in headless mode (without opening a browser window)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

# Function to get tweets for a given movie
def get_movie_reviews(movie_name):
    driver = setup_driver()
    
    # URL for the Twitter search
    search_url = f"https://twitter.com/search?q={movie_name}&src=typed_query&f=live"
    driver.get(search_url)

    time.sleep(3)  # Wait for the page to load

    # Scroll down to load more tweets (simulate user behavior)
    for _ in range(3):  # Scroll three times (you can adjust for more tweets)
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
        time.sleep(3)

    # Get page content after scrolling
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Extract tweets
    tweets = soup.find_all('div', {'data-testid': 'tweet'})
    
    reviews = []
    for tweet in tweets:
        try:
            user = tweet.find('span', {'class': 'css-901oao'}).get_text()
            tweet_text = tweet.find('div', {'lang': True}).get_text()
            reviews.append({
                'user': user,
                'tweet': tweet_text
            })
        except AttributeError:
            continue  # Skip any tweets that don't have the right format

    driver.quit()

    return reviews

# Main function
def main():
    movie_name = input("Enter the name of the new movie: ")
    
    # Fetch and display the reviews
    reviews = get_movie_reviews(movie_name)
    
    if reviews:
        print(f"\nFirst few tweets about '{movie_name}':\n")
        for i, review in enumerate(reviews[:30], 1):  # Limit to 30 tweets
            print(f"{i}. @{review['user']} said: {review['tweet']}\n")
    else:
        print(f"No tweets found for {movie_name}.")

if __name__ == "__main__":
    main()
