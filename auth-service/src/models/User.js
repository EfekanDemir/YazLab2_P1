const mongoose = require('mongoose');

const userSchema = new mongoose.Schema({
  username: {
    type: String,
    required: true,
    unique: true,
    trim: true
  },
  password: {
    type: String,
    required: true
  },
  tokens: [{
    type: String,
    required: true
  }],
  role: {
    type: String,
    enum: ['admin', 'customer', 'anonymous'],
    default: 'admin'
  }
}, { 
  timestamps: true 
});

module.exports = mongoose.model('User', userSchema);
