# AI News Aggregator

An intelligent, full-stack news aggregation platform powered by AI. It provides an intuitive interface to browse news, read AI-generated summaries, interact with articles via a Q&A chat, and extract social media references from the content.

## Architecture

The project is built using a modern microservice-like architecture separating frontend, backend, and the AI processing service.

1. **Frontend (Angular)**: The user interface is developed with **Angular 21** and Angular Material for a responsive, modern experience.
2. **Backend (Node.js & Express)**: A RESTful API built with **Express** and **Mongoose** to handle user authentication (JWT), data persistence in MongoDB, and route requests.
3. **AI Service (Python & Flask)**: A specialized service leveraging **LangChain**, **Chromadb**, and the **Groq API (Llama 3.3 70B)** to provide advanced features like:
   - Batch and individual article summarization.
   - Retrieval-Augmented Generation (RAG) for answering questions strictly based on article contexts.
   - Generation of suggested questions for readers.
   - Automated extraction of Twitter/X and Instagram links embedded in article content.

## Project Structure

```text
ai-news-aggregator/
├── frontend/      # Angular application
├── backend/       # Node.js/Express server API
└── ai-service/    # Python/Flask microservice for AI processing
```

## Features

- **User Authentication**: Secure JWT-based login and registration.
- **Smart Summaries**: AI automatically condenses long news pieces into concise bullet points.
- **Interactive Q&A**: Ask questions about specific articles, and AI will provide contextual answers.
- **Social Media Extraction**: Readily exposes any embedded social links (e.g., Twitter/X) from full news texts.

## Getting Started

### Prerequisites

- [Node.js](https://nodejs.org/) & npm
- [Angular CLI](https://angular.io/cli) (`npm install -g @angular/cli`)
- [Python 3.8+](https://www.python.org/)
- [MongoDB](https://www.mongodb.com/) (Local or Atlas)
- [Groq API Key](https://console.groq.com/)

### Installation & Execution

You will need to run all three services concurrently for the full application to work.

#### 1. Backend Service
Configure your MongoDB connection and JWT secret before starting.
```bash
cd backend
npm install
npm run dev
```
*(Requires a `.env` file containing variables like `MONGO_URI` and `JWT_SECRET`)*

#### 2. AI Service
Provides the intelligence layer running on port `5000`.
```bash
cd ai-service
pip install -r requirements.txt
python app.py
```
*(Requires a `.env` file containing `GROQ_API_KEY=your_api_key_here`)*

#### 3. Frontend Web App
Start the Angular UI. This will compile the application and serve it on port `4200`.
```bash
cd frontend
npm install
npm start
```

## Environment Variables

To properly run the application, ensure the following `.env` files are configured:

**`backend/.env`**
```env
PORT=3000
MONGODB_URI=your_mongodb_connection_string
JWT_SECRET=your_jwt_secret_key
```

**`ai-service/.env`**
```env
GROQ_API_KEY=your_groq_api_key
```

## Tech Stack

- **Frontend:** Angular, TypeScript, Angular Material
- **Backend:** Node.js, Express, MongoDB, Mongoose, Axios, bcryptjs
- **AI Service:** Python, Flask, LangChain, Groq (Llama), HuggingFace Embeddings (all-MiniLM-L6-v2), Chroma, Newspaper3k
