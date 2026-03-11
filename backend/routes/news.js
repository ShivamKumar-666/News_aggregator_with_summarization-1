const express = require('express');
const router = express.Router();
const axios = require('axios');
router.get('/', async (req, res) => {
  const category = req.query.category || 'general';
  console.log('Route hit! Category:', category);
  console.log('Key:', process.env.NEWSAPI_KEY);
  try {
    const newsRes = await axios.get('https://newsapi.org/v2/top-headlines', {
      headers: {
        'User-Agent': 'Mozilla/5.0',
        'X-Api-Key': process.env.NEWSAPI_KEY,
      },
      params: {
        country: 'us',
        category: category,
        pageSize: 9,
      },
    });

    const articles = newsRes.data.articles
      .filter((a) => a.title && a.title !== '[Removed]')
      .map((a) => ({
        title: a.title,
        description: a.description,
        content: a.content,
        url: a.url,
        image: a.urlToImage,
        source: { name: a.source.name },
        publishedAt: a.publishedAt,
      }));

    return res.json({ articles });
  } catch (error) {
    console.error('Status:', error.response?.status);
    console.error('Error data:', JSON.stringify(error.response?.data));
    res.status(500).json({ message: 'Failed to fetch news' });
  }
});

// RAG-based Q&A
router.post('/ask', async (req, res) => {
  const { question, category } = req.body;
  try {
    const aiRes = await axios.post(`${process.env.AI_SERVICE_URL}/ask`, {
      question,
      category,
    });
    res.json(aiRes.data);
  } catch (error) {
    res.status(500).json({ message: 'Failed to get answer' });
  }
});

// Article-specific Q&A
router.post('/ask-article', async (req, res) => {
  const { question, article, history } = req.body;
  console.log('Ask-article request:', { question, articleTitle: article?.title, historyLength: history?.length });
  try {
    const aiRes = await axios.post(`${process.env.AI_SERVICE_URL}/ask-article`, {
      question,
      article,
      history,
    });
    res.json(aiRes.data);
  } catch (error) {
    console.error('AI Service Error:', error.response?.data || error.message);
    res.status(500).json({ message: 'Failed to get answer', error: error.message });
  }
});

// Suggest questions for article
router.post('/suggest-questions', async (req, res) => {
  const { article } = req.body;
  try {
    const aiRes = await axios.post(`${process.env.AI_SERVICE_URL}/suggest-questions`, { article });
    res.json(aiRes.data);
  } catch (error) {
    res.json({ questions: ["What is this about?", "Tell me more", "Summarize this"] });
  }
});

// Summarize Single Article & Extract Socials
router.post('/summarize-single-article', async (req, res) => {
  const { article } = req.body;
  try {
    const aiRes = await axios.post(`${process.env.AI_SERVICE_URL}/summarize-single-article`, { article });
    res.json(aiRes.data);
  } catch (error) {
    console.error('Error in summarize single article:', error.response?.data || error.message);
    res.status(500).json({ summary: "Failed to generate summary.", socials: [] });
  }
});

module.exports = router;