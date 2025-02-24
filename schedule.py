import logging
from processing_articles import CompactNewsAgent
from caller import postToBlogger
import time
from datetime import datetime

# Configure logging
logging.basicConfig(
    filename='news_schedule.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

topics = [
    "India",
    "World",  # Fixed missing comma
    "Sports",
    "Latest News"
]

def process_news():
    try:
        agent = CompactNewsAgent(limit=8)
    except Exception as e:
        logging.error(f"Failed to initialize CompactNewsAgent: {e}")
        return

    logging.info(f"Starting news processing at {datetime.now()}")
    
    for topic in topics:
        try:
            result = agent.process_feed(topic)
            if result:
                for article in result:
                    try:
                        article["topics"] = topic
                        postToBlogger(article)
                        logging.info(f"Successfully posted article for topic: {topic}")
                        time.sleep(60)  # 60 second delay between posts
                    except Exception as e:
                        logging.error(f"Error posting article for topic {topic}: {e}")
        except Exception as e:
            logging.error(f"Error processing topic {topic}: {e}")
            continue

    logging.info(f"Completed news processing at {datetime.now()}")

if __name__ == "__main__":
    process_news()