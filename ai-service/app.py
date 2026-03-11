from flask import Flask, request, jsonify
from flask_cors import CORS
from rag_pipeline import build_vector_store, summarize_articles_batch, answer_question, answer_article_question, generate_suggested_questions

app = Flask(__name__)
CORS(app)


@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "AI Service Running!"})


@app.route("/summarize", methods=["POST"])
def summarize():
    data = request.json
    articles = data.get("articles", [])
    category = data.get("category", "general")

    if not articles:
        return jsonify({"error": "No articles provided"}), 400

    # Build RAG vector store
    build_vector_store(articles, category)

    # Batch summarize all articles in ONE Groq call
    summaries = summarize_articles_batch(articles)

    summarized = []
    for i, article in enumerate(articles):
        summary = summaries.get(i+1, article.get('description', 'No summary available.'))
        summarized.append({
            "title": article.get("title", ""),
            "summary": summary,
            "url": article.get("url", ""),
            "image": article.get("image", ""),
            "source": article.get("source", {}).get("name", ""),
            "publishedAt": article.get("publishedAt", ""),
        })

    return jsonify({"articles": summarized, "category": category})

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    question = data.get("question", "")
    category = data.get("category", "general")

    if not question:
        return jsonify({"error": "No question provided"}), 400

    result = answer_question(question, category)
    return jsonify(result)


@app.route("/ask-article", methods=["POST"])
def ask_article():
    try:
        data = request.json
        print("Received data:", data)
        question = data.get("question", "")
        article = data.get("article", {})
        history = data.get("history", [])
        print(f"Question: {question}, History Length: {len(history)}")
        print(f"Article title: {article.get('title', 'N/A')}")

        if not question:
            return jsonify({"error": "No question provided"}), 400

        result = answer_article_question(question, article, history)
        return jsonify(result)
    except Exception as e:
        print(f"Error in ask_article: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/suggest-questions", methods=["POST"])
def suggest_questions():
    try:
        data = request.json
        article = data.get("article", {})
        questions = generate_suggested_questions(article)
        return jsonify({"questions": questions})
    except Exception as e:
        print(f"Error generating questions: {str(e)}")
        return jsonify({"questions": ["What is this about?", "Tell me more", "Summarize this"]}), 200


@app.route("/summarize-single-article", methods=["POST"])
def summarize_single_article():
    try:
        data = request.json
        article = data.get("article", {})
        
        if not article:
            return jsonify({"error": "No article provided"}), 400
            
        from rag_pipeline import summarize_and_extract_socials
        result = summarize_and_extract_socials(article)
        return jsonify(result)
    except Exception as e:
        print(f"Error in summarize_single_article: {str(e)}")
        return jsonify({"summary": "Could not generate summary.", "socials": []}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)