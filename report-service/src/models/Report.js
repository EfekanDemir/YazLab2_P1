const mongoose = require('mongoose');

const reportSchema = new mongoose.Schema({
  title: {
    type: String,
    required: true,
    trim: true
  },
  generatedAt: {
    type: Date,
    default: Date.now
  },
  productCount: {
    type: Number,
    required: true,
    default: 0
  },
  totalStockValue: {
    type: Number,
    required: true,
    default: 0
  },
  // Snapshot olarak kaydedilen (ref içermeyen, donmuş) ürün listesi
  products: {
    type: Array,
    required: true,
    default: []
  }
});

module.exports = mongoose.model('Report', reportSchema);
