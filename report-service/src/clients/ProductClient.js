const axios = require('axios');

class ProductClient {
  constructor() {
    // Docker default hostname and port for product-service
    this.baseURL = process.env.PRODUCT_SERVICE_URL || 'http://product-service:3000/products';
  }

  async getProducts() {
    try {
      const response = await axios.get(this.baseURL, {
        headers: {
          'x-internal-request': 'true'
        }
      });
      return response.data;
    } catch (error) {
      const err = new Error('Failed to fetch data from Product Service');
      err.statusCode = error.response ? error.response.status : 502; // 502 Bad Gateway if service is down
      throw err;
    }
  }
}

module.exports = ProductClient;
