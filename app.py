from dotenv import load_dotenv
load_dotenv()
import time
import gradio as gr
from processing_articles import CompactNewsAgent
from caller import postToBlogger

topics = [
    "India",
    "World"
    "Sports",
    "Latest News"
]

def process_news():
    for topic in topics:
        try:
            result = agent.process_feed(topic)
            if result:
                for article in result:
                    article["topics"] = topic
                    postToBlogger(article)
                    # Add 60 second delay after each post
                    time.sleep(60)  
        except Exception as e:
            print(f"Error processing topic {topic}: {e}")
        except Exception as e:
            print(f"Error writing to JSON file: {e}")


def button_click():
    try:
        fl = open("articles.json", "w")
        fl.write("[]")
        fl.close()
        process_news()
        return "News processing completed successfully and posted also!"
    except Exception as e:
        return f"Error occurred: {str(e)}"

agent = CompactNewsAgent(limit=1)

# Create Gradio interface
demo = gr.Interface(
    fn=button_click,
    inputs=[],
    outputs=gr.Textbox(label="Status"),
    title="News Processing System",
    description="Click the button to process news articles"
)

if __name__ == "__main__":
    demo.launch()