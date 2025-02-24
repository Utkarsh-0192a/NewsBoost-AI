import logging
import feedparser
from newspaper import Article
import requests
import time
import random
import configparser
import os
import re
from huggingface_hub import InferenceClient
from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
class CompactNewsAgent:
    def __init__(self, limit=1):
        try:
            self.limit = limit
            self.api_token = os.getenv('HUGGINGFACE_API_TOKEN')
            if not self.api_token:
                raise ValueError("HUGGINGFACE_API_TOKEN not found in environment variables")
            self.client = InferenceClient(provider="hf-inference",api_key=self.api_token)
            self.model_id = "google/gemma-2-2b-it"


        except Exception as e:
            logging.error(f"Failed to initialize HF client: {e}")
            raise

        # Load configuration
        config = configparser.ConfigParser()
        config.read('config.ini')

        self.link_path = "rss_links_final.json"
        self.output_dir = "articles_html"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        # Load RSS feeds url
        links = [
        "http://timesofindia.indiatimes.com/rssfeeds/-2128936835.cms",
        "http://timesofindia.indiatimes.com/rssfeeds/296589292.cms",
        "http://timesofindia.indiatimes.com/rssfeeds/4719148.cms",
        "https://www.hindustantimes.com/feeds/rss/elections/rssfeed.xml",
        "https://www.hindustantimes.com/feeds/rss/latest/rssfeed.xml"
        ]

        dict_links = {
            "India": links[0],
            "World": links[1],
            "Sports": links[2],
            "Elections 2025": links[3],
            "Latest News": links[4]
        }
        self.rss_feeds = dict_links
        
        self.USER_AGENT = config.get('scraper', 'user_agent', fallback='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        self.MAX_RETRIES = config.getint('scraper', 'max_retries', fallback=3)
        self.BACKOFF_FACTOR = config.getfloat('scraper', 'backoff_factor', fallback=0.3)
        self.NUM_THREADS = config.getint('scraper', 'num_threads', fallback=4)

    def process_article(self, text):
        try:
            logging.info("Processing article with Hugging Face model...")
            news_title, news_topic, news_article = text
            
            # Truncate long articles
            news_article = news_article[:5000] if news_article else ""
            
            prompt = f"""
                You are an expert SEO content writer and journalist. Your task is to summarize and optimize a given news article for SEO.
            **Title**: {news_title}  
            **Topic**: {news_topic}  
            **Text**: {news_article}  
            #### **SEO Requirements:**  
            - Generate a **concise summary** (200 words max).   
            - Add a **meta description** (100 character).
            - Use **H1 & H2 headings** for structure.  
            - Improve **readability** with short sentences & paragraphs.  
            - Use **bullet points** for clarity.
            #### **🔹 Output Format (Structured SEO optimised summary)
            ```markdown
            # [news_title]
            ## Summary  
            [summary_text]
            ##meta description
            [meta_description]
            """
            
            try:
                completion = self.client.chat.completions.create(
                    model="google/gemma-2-2b-it",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=2000
                )
                
                output = completion.choices[0].message.content
            except Exception as e:
                logging.error(f"API generation error: {e}")
                return None
            
            result = self.parse_response(output)

            logging.info("Generated summary successfully")
            return result
        
        except Exception as e:
            logging.error(f"Article processing error: {e}")
            return None

    def parse_response(self, markdown_text):
        # Extract the title from the first "# " header
        title_match = re.search(r'^# (.+)', markdown_text, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else ""
        
        # Extract the summary content under the "## Summary" heading
        summary_match = re.search(r'## Summary\s*(.*?)\s*(?=^## |\Z)', markdown_text, re.MULTILINE | re.DOTALL)
        summary = summary_match.group(1).strip() if summary_match else ""
        
        # Extract the meta description under the "## Meta Description" heading
        meta_match = re.search(r'## Meta Description\s*(.*?)\s*(?=^## |\Z)', markdown_text, re.MULTILINE | re.DOTALL)
        meta_description = meta_match.group(1).strip() if meta_match else ""
        
        return {
            "title": title,
            "content": summary,
            "metaDescription": meta_description
        }
    
    def fetch_rss(self, feed_url):
        """Fetch and parse RSS feed"""
        try:
            feed = feedparser.parse(feed_url)
            if feed.bozo:  # feedparser error indicator
                logging.error(f"Feed parsing error: {feed.bozo_exception}")
                return []
                
            articles = []
            for entry in feed.entries[:self.limit]:
                try:
                    response = self.fetch_with_retries(entry.link)
                    article = Article(entry.link)
                    article.download(input_html=response.text)
                    article.parse()
                    text = article.text
                    if not text:
                        logging.warning(f"No text content found for {entry.link}")
                        continue
                        
                    articles.append({
                        "title": entry.title,
                        "link": entry.link,
                        "published": getattr(entry, 'published', ''),
                        "text": text
                    })
                except Exception as e:
                    logging.error(f"Error extracting content from {entry.link}: {str(e)}")
                    continue
                    
            return articles
            
        except Exception as e:
            logging.error(f"Error fetching or parsing RSS feed: {e}")
            return []

    def fetch_with_retries(self, url):
        """Fetch URL with retries and exponential backoff"""
        headers = {'User-Agent': self.USER_AGENT}
        for attempt in range(self.MAX_RETRIES):
            try:
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                return response
            except requests.exceptions.RequestException as e:
                logging.error(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt < self.MAX_RETRIES - 1:
                    sleep_time = self.BACKOFF_FACTOR * (2 ** attempt) + random.uniform(0, 1)
                    logging.info(f"Retrying in {sleep_time:.2f} seconds...")
                    time.sleep(sleep_time)
                else:
                    raise

    def process_feed(self, category):
        """Process a single RSS feed."""
        try:
            feed_url = self.rss_feeds.get(category)
            if not feed_url:
                return f"Error: Invalid category '{category}'"
                
            logging.info(f"Processing feed: {feed_url}")
            
            articles = self.fetch_rss(feed_url)
            if not articles:
                return f"Error: No articles found for {category}"
                
            successes = []
            for article in articles:
                try:
                    dat = [article['title'], category, article['text']]
                    summary = self.process_article(dat)
                    if summary:
                        successes.append(summary)
                except Exception as e:
                    logging.error(f"Error processing article: {e}")
                    continue
                    
            if not successes:
                return f"Error: Could not process any articles for {category}"
            return successes  # Return first successful summary
            
        except Exception as e:
            logging.error(f"Error processing feed {category}: {e}")
            return f"Error processing feed: {str(e)}"

if __name__ == "__main__":
    agent = CompactNewsAgent(limit=5)
    topics = ["Latest News"]
    logging.info(f"Topics selected: {topics}")
    for topic in topics:
        print(agent.process_feed(topic))
