const ProductService = require('../services/ProductService');
const MongoProductRepository = require('../repositories/MongoProductRepository');

// Instantiate dependencies
const productRepository = new MongoProductRepository();
const productService = new ProductService(productRepository);

class ProductController {
  
  static async getAll(req, res) {
    try {
      const products = await productService.getAllProducts();
      return res.status(200).json(products);
    } catch (error) {
      const status = error.statusCode || 500;
      return res.status(status).json({ message: error.message || 'Internal Server Error' });
    }
  }

  static async getById(req, res) {
    try {
      const { id } = req.params;
      const product = await productService.getProductById(id);
      return res.status(200).json(product);
    } catch (error) {
      // Catching 404 from Service
      const status = error.statusCode || 500;
      return res.status(status).json({ message: error.message || 'Internal Server Error' });
    }
  }

  static async create(req, res) {
    try {
      const { name, price } = req.body;
      
      // Basic validation mapped to 400 Bad Request
      if (!name || price === undefined) {
        return res.status(400).json({ message: 'Name and price are required' });
      }

      const newProduct = await productService.createProduct(req.body);
      // RMM Level 2 -> 201 Created
      return res.status(201).json(newProduct);
    } catch (error) {
      const status = error.statusCode || 500;
      return res.status(status).json({ message: error.message || 'Internal Server Error' });
    }
  }

  static async update(req, res) {
    try {
      const { id } = req.params;
      const updatedProduct = await productService.updateProduct(id, req.body);
      return res.status(200).json(updatedProduct);
    } catch (error) {
      const status = error.statusCode || 500;
      return res.status(status).json({ message: error.message || 'Internal Server Error' });
    }
  }

  static async delete(req, res) {
    try {
      const { id } = req.params;
      await productService.deleteProduct(id);
      
      // RMM Level 2 -> 204 No Content
      // Send() without arguments since 204 should not have a response body
      return res.status(204).send();
    } catch (error) {
      const status = error.statusCode || 500;
      return res.status(status).json({ message: error.message || 'Internal Server Error' });
    }
  }
}

module.exports = ProductController;
