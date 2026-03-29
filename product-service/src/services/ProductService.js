class ProductService {
  constructor(productRepository) {
    this.productRepository = productRepository;
  }

  async getAllProducts() {
    return await this.productRepository.findAll();
  }

  async getProductById(id) {
    const product = await this.productRepository.findById(id);
    if (!product) {
      const error = new Error('Product not found');
      error.statusCode = 404;
      throw error;
    }
    return product;
  }

  async createProduct(productData) {
    // We can add extra validation logic here if needed (e.g., check negative stock before DB layer catches it)
    if (productData.price < 0) {
      const error = new Error('Price cannot be negative');
      error.statusCode = 400;
      throw error;
    }
    return await this.productRepository.create(productData);
  }

  async updateProduct(id, productData) {
    // Check existence first
    await this.getProductById(id); 

    // Partial update allowed
    const updatedProduct = await this.productRepository.update(id, productData);
    return updatedProduct;
  }

  async deleteProduct(id) {
    await this.getProductById(id);
    await this.productRepository.delete(id);
    return true;
  }
}

module.exports = ProductService;
