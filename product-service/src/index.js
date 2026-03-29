require('dotenv').config();
const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const productRoutes = require('./routes/productRoutes');

const app = express();
const PORT = process.env.PORT || 3000;
const MONGODB_URI = process.env.MONGODB_URI;

// Built-in middleware
app.use(express.json());
app.use(cors());

// Routes
// Gateway calls to http://product-service:3000/products will be mapped here.
// You could also mount it at '/products', depending on how gateway strips prefixes.
// Assuming dispatcher proxies /products directly.
app.use('/products', productRoutes);

// Health check endpoint (for docker-compose / orchestration)
app.get('/health', (req, res) => {
  res.status(200).json({ status: 'UP', service: 'product-service' });
});

// App Startup
const start = async () => {
  if (!MONGODB_URI) {
    console.error('Fatal Error: MONGODB_URI is not defined.');
    process.exit(1);
  }

  try {
    await mongoose.connect(MONGODB_URI, {
      useNewUrlParser: true,
      useUnifiedTopology: true
    });
    console.log('Connected to MongoDB (product_db)');

    app.listen(PORT, () => {
      console.log(`Product Service is running on port ${PORT}`);
    });
  } catch (error) {
    console.error('Database connection failed', error);
    process.exit(1);
  }
};

start();
