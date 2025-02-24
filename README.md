---
title: Autonews
emoji: 💻
colorFrom: pink
colorTo: pink
sdk: gradio
sdk_version: 5.17.1
app_file: app.py
pinned: false
short_description: get news and post them
---

Check out the configuration reference at https://huggingface.co/docs/hub/spaces-config-reference

# AutoNews - Automated News Aggregator and Publisher

AutoNews is an automated system that fetches news from various RSS feeds, processes them using AI, and publishes them to a Blogger blog.

## Author & Developer
Developed by Utkarsh Gautam

## Features

- RSS feed aggregation from multiple sources (Times of India, Hindustan Times)
- AI-powered article summarization using Hugging Face's Gemma-2-2b model
- Automated publishing to Blogger platform
- SEO optimization of content
- Simple Gradio web interface

## Prerequisites

- Python 3.8+
- Hugging Face API token
- Google OAuth2 credentials for Blogger API
- Virtual environment (recommended)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd autonews
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file with:
```
HUGGINGFACE_API_TOKEN=your_token
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_PROJECT_ID=your_project_id
GOOGLE_CLIENT_SECRET=your_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8080/
```

## Configuration

1. RSS Feeds:
- Edit `processing_articles.py` to modify RSS feed sources
- Current sources include Times of India and Hindustan Times sections

2. Blogger Setup:
- Place your `client_secret.json` in the root directory
- Run the app once to authenticate with Google

## Usage

1. Start the Gradio interface:
```bash
python app.py
```

2. Access the web interface at `http://localhost:7860`

3. Click the button to:
- Fetch latest news articles
- Process and summarize content
- Post to your Blogger blog

## How It Works

1. **News Fetching (`processing_articles.py`)**:
   - Fetches RSS feeds from configured sources
   - Extracts article content using newspaper3k
   - Implements retry mechanism with exponential backoff

2. **AI Processing**:
   - Uses Hugging Face's Gemma-2-2b model
   - Generates SEO-optimized summaries
   - Creates meta descriptions

3. **Publishing (`caller.py`)**:
   - Authenticates with Blogger API
   - Posts processed articles
   - Handles rate limiting

## Deployment

The application can be deployed on Hugging Face Spaces:

1. Create a new Space on Hugging Face
2. Configure the Space settings using the provided `README.md` front matter
3. Push your code to the Space's repository

## Contributing

Contributions are welcome! Please feel free to submit pull requests.


