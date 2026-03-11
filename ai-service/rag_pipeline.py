import os
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from groq import Groq
from newspaper import Article
import requests

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
groq_client = Groq(api_key=GROQ_API_KEY)

# Load embedding model once at startup
print("Loading embedding model...")
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
print("Embedding model loaded!")

text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

# In-memory vector store per category
vector_stores = {}


def build_vector_store(articles, category="general"):
    docs = []
    metadatas = []

    for article in articles:
        content = f"{article.get('title', '')}. {article.get('description', '')} {article.get('content', '')}"
        chunks = text_splitter.split_text(content)
        for chunk in chunks:
            docs.append(chunk)
            metadatas.append({
                "title": article.get("title", ""),
                "url": article.get("url", ""),
                "source": article.get("source", {}).get("name", ""),
            })

    if not docs:
        return None

    store = Chroma.from_texts(
        texts=docs,
        embedding=embeddings,
        metadatas=metadatas,
        collection_name=f"news_{category}",
    )
    vector_stores[category] = store
    return store


def summarize_articles_batch(articles):
    combined = ""
    for i, article in enumerate(articles):
        title = article.get('title', '')
        content = article.get('description', '') or article.get('content', '')
        combined += f"\nArticle {i+1}:\nTitle: {title}\nContent: {content}\n"

    prompt = f"""Summarize each of the following news articles in 2 sentences each.
Return a JSON array like: [{{"index": 1, "summary": "..."}}, ...]
Only return the JSON, nothing else.

{combined}"""

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2000,
    )
    import json
    text = response.choices[0].message.content.strip()
    try:
        summaries = json.loads(text)
        return {s['index']: s['summary'] for s in summaries}
    except:
        return {}


def answer_question(question, category="general"):
    store = vector_stores.get(category)
    if not store:
        return "Please load news for this category first before asking questions."

    # Retrieve relevant chunks
    retriever = store.as_retriever(search_kwargs={"k": 4})
    relevant_docs = retriever.invoke(question)

    context = "\n\n".join([doc.page_content for doc in relevant_docs])
    sources = list({doc.metadata.get("title", "") for doc in relevant_docs})

    prompt = f"""You are a helpful news assistant. Answer the question based ONLY on the news context below.
If the answer is not in the context, say "I don't have enough information on this topic."

Context:
{context}

Question: {question}

Answer:"""

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300,
    )

    return {
        "answer": response.choices[0].message.content.strip(),
        "sources": sources[:3],
    }


def generate_suggested_questions(article):
    title = article.get('title', '') or ''
    summary = article.get('summary', '') or ''
    description = article.get('description', '') or ''
    content = article.get('content', '') or ''
    
    context = f"Title: {title}\nSummary: {summary}\nDescription: {description}\nSnippet: {content}"

    prompt = f"""Based on this news article, generate 3 short, relevant questions that CAN BE FULLY ANSWERED using ONLY the information provided in the text below.
Do not suggest questions if the answer is not present in the text.
Return ONLY a JSON array of strings like: ["question 1?", "question 2?", "question 3?"]
No other text.

Article:
{context}"""

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.3
        )
        
        import json
        questions = json.loads(response.choices[0].message.content.strip())
        return questions[:3]
    except Exception as e:
        print(f"Error generating questions: {str(e)}")
        return ["What are the main points of this article?", "Who or what is the main subject?", "What is the key takeaway?"]


from newspaper import Article
import requests

def fetch_full_article(url):
    if not url:
        return None
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        res = requests.get(url, headers=headers, timeout=(3.05, 3))
        if res.status_code == 200:
            article = Article(url)
            article.set_html(res.text)
            article.parse()
            return {"text": article.text, "html": res.text}
        return None
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return None


def answer_article_question(question, article, history=None):
    if history is None:
        history = []
        
    # Try to fetch full article content
    article_data = fetch_full_article(article.get('url', ''))
    full_text = article_data.get('text', '') if article_data else ''
    
    # Extract all available fields
    title = article.get('title', '') or ''
    summary = article.get('summary', '') or ''
    description = article.get('description', '') or ''
    content = article.get('content', '') or ''
    
    # Combine fields to maximize context
    context = f"Title: {title}\nSummary: {summary}\nDescription: {description}\nSnippet: {content}"
    
    if full_text and len(full_text) > 100:
        context += f"\nFull Article Text: {full_text[:4000]}"
        
    # Format message history
    history_str = ""
    if history:
        history_str = "\nConversation History:\n"
        for msg in history:
            role = "User" if msg.get("type") == "user" else "AI"
            history_str += f"{role}: {msg.get('text')}\n"

    prompt = f"""You are an insightful AI news assistant. The user is asking a question about a specific news article.
Answer the question based ONLY on the provided article context below.
If the answer is definitely not contained in the context, say "I don't have enough information in this article to answer that."
Be concise and helpful.

Article Context:
{context}
{history_str}

User's Question: {question}

Answer:"""

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
            temperature=0.3
        )
        return {"answer": response.choices[0].message.content.strip()}
    except Exception as e:
        print(f"Error generating answer: {str(e)}")
        return {"answer": "Sorry, I am having trouble connecting to my AI brain right now."}

def summarize_and_extract_socials(article):
    # Try to fetch full article content
    article_data = fetch_full_article(article.get('url', ''))
    full_text = article_data.get('text', '') if article_data else ''
    html_content = article_data.get('html', '') if article_data else ''
    
    import re
    social_urls = []
    if html_content:
        pattern = r'https?://(?:www\.)?(?:twitter\.com|x\.com|instagram\.com)/[a-zA-Z0-9_/?=&#.-]+'
        found = re.findall(pattern, html_content)
        for u in found:
            if 'intent' not in u.lower() and 'share' not in u.lower() and 'privacy' not in u.lower() and u not in social_urls:
                parts = u.split('/')
                if len(parts) > 3 and parts[3]:
                    social_urls.append(u)
    
    # Extract all available fields
    title = article.get('title', '') or ''
    summary = article.get('summary', '') or ''
    description = article.get('description', '') or ''
    content = article.get('content', '') or ''
    
    # Combine fields to maximize context
    context = f"Title: {title}\nSummary: {summary}\nDescription: {description}\nSnippet: {content}"
    
    if full_text and len(full_text) > 100:
        context += f"\nFull Article Text: {full_text[:4000]}"
        
    if social_urls:
        context += f"\nFound Social Media Links in Article HTML: {', '.join(social_urls)}"
        
    prompt = f"""You are an insightful AI news assistant. The user wants a detailed, bulleted summary of the following news article, AND a list of any X (Twitter) or Instagram URLs that are explicitly referenced or embedded in the article text.

If there are NO X (Twitter) or Instagram URLs in the text, return an empty array for 'socials'.
Return your response ONLY as a valid JSON object matching this exact format, with NO Markdown wrappers outside the JSON:
{{
  "summary": "A SINGLE STRING containing your detailed 3-5 bullet point summary. Do NOT use raw newlines inside this string, use the '\\n' character sequence instead.",
  "socials": ["url1", "url2"]
}}
Do not include any extra conversational text. The 'summary' field MUST be a single string, not an array.

Article Context:
{context}"""

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
            temperature=0.2
        )
        import json
        text = response.choices[0].message.content.strip()
        if text.startswith('```json'): text = text[7:-3]
        elif text.startswith('```'): text = text[3:-3]
        result = json.loads(text.strip(), strict=False)
        return {
            "summary": result.get("summary", "Could not generate summary."),
            "socials": result.get("socials", [])
        }
    except Exception as e:
        print(f"Error generating summary & socials: {str(e)}")
        return {"summary": "Sorry, an error occurred while summarizing the article.", "socials": []}
