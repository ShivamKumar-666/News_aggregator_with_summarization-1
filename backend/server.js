const express = require('express');
const dotenv = require('dotenv');
const cors = require('cors');
const connectDB = require('./config/db');

dotenv.config();
dotenv.config();
console.log('NEWSAPI_KEY loaded:', process.env.NEWSAPI_KEY);
connectDB();

const app = express();
app.use(cors());
app.use(express.json());

app.use('/api/auth', require('./routes/auth'));
app.use('/api/news', require('./routes/news'));

app.get('/', (req, res) => res.send('AI News Aggregator API Running'));

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
