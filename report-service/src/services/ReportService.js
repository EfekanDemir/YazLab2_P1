class ReportService {
  constructor(reportRepository, productClient) {
    this.reportRepository = reportRepository;
    this.productClient = productClient;
  }

  async getAllReports() {
    return await this.reportRepository.findAll();
  }

  async getReportById(id) {
    const report = await this.reportRepository.findById(id);
    if (!report) {
      const error = new Error('Report not found');
      error.statusCode = 404;
      throw error;
    }
    return report;
  }

  async createReport(title) {
    // 1. Fetch current live data from product-service
    const products = await this.productClient.getProducts();

    // 2. Map-reduce logic for totalStockValue
    const totalStockValue = products.reduce((sum, item) => {
      // safely handle cases where price or stock might be undefined
      const price = item.price || 0;
      const stock = item.stock || 0;
      return sum + (price * stock);
    }, 0);

    const productCount = products.length;

    // 3. Optional generate default title if null
    const finalTitle = title || `Rapor - ${new Date().toISOString()}`;

    // 4. Save the snapshot
    const reportData = {
      title: finalTitle,
      productCount,
      totalStockValue,
      products // This stores the whole snapshot inside Document
    };

    return await this.reportRepository.create(reportData);
  }

  async deleteReport(id) {
    await this.getReportById(id); // Throws 404 if not exists
    await this.reportRepository.delete(id);
    return true;
  }
}

module.exports = ReportService;
