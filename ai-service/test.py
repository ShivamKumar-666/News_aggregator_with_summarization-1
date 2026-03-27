import os
from groq import Groq
import json
import requests
from dotenv import load_dotenv

load_dotenv()

NEWSAPI_KEY = os.getenv('NEWSAPI_KEY')
res = requests.get(f'https://newsapi.org/v2/top-headlines?country=us&pageSize=1', headers={'X-Api-Key': NEWSAPI_KEY, 'User-Agent': 'Mozilla/5.0'})
article = res.json()['articles'][0]

print('Article Title:', article.get('title'))

from rag_pipeline import summarize_and_extract_socials
result = summarize_and_extract_socials(article)

print(json.dumps(result, indent=2))
