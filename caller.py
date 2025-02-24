import httplib2
import json
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run_flow
from googleapiclient import discovery

# Authorize and get credentials using OAuth2
def authorize_credentials():
    CLIENT_SECRET = 'client_secret.json'
    SCOPE = 'https://www.googleapis.com/auth/blogger'
    STORAGE = Storage('credentials.storage')
    credentials = STORAGE.get()
    if credentials is None or credentials.invalid:
        flow = flow_from_clientsecrets(CLIENT_SECRET, scope=SCOPE)
        http = httplib2.Http()
        credentials = run_flow(flow, STORAGE, http=http)
    return credentials

# Build the Blogger service
def getBloggerService():
    credentials = authorize_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = 'https://blogger.googleapis.com/$discovery/rest?version=v3'
    service = discovery.build('blogger', 'v3', http=http, discoveryServiceUrl=discoveryUrl)
    return service

# Post a single article to Blogger
def postToBlogger(payload):
    service = getBloggerService()
    post = service.posts()
    insert = post.insert(blogId='5944176616384960152', body=payload).execute()
    print("Done post! Posted:", insert.get("title"))
    return insert

# Process the articles.json file and post each article
def processArticlesJson(filename):
    with open(filename, "r", encoding="utf-8") as f:
        articles = json.load(f)
    for article in articles:
        payload = {
            "title": article.get("title", "No Title"),
            "content": article.get("content", ""),
            "labels": article.get("topics", []),
            "customMetaData": article.get("metaDescription", "")
        }
        postToBlogger(payload)

if __name__ == "__main__":
    processArticlesJson("articles.json")
