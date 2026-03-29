const IProductRepository = require('./IProductRepository');
const Product = require('../models/Product');

class MongoProductRepository extends IProductRepository {
  constructor() {
    super();
  }

  async findAll() {
    return await Product.find({});
  }

  async findById(id) {
    return await Product.findById(id);
  }

  async create(productData) {
    const product = new Product(productData);
    return await product.save();
  }

  async update(id, productData) {
    // new: true döner güncellenmiş data
    return await Product.findByIdAndUpdate(id, productData, { new: true });
  }

  async delete(id) {
    return await Product.findByIdAndDelete(id);
  }
}

module.exports = MongoProductRepository;
