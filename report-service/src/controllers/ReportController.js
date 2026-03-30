const ReportService = require('../services/ReportService');
const MongoReportRepository = require('../repositories/MongoReportRepository');
const ProductClient = require('../clients/ProductClient');

// Resolve dependencies manually (Poor man's constructor injection)
const reportRepository = new MongoReportRepository();
const productClient = new ProductClient();
const reportService = new ReportService(reportRepository, productClient);

class ReportController {
  
  static async getAll(req, res) {
    try {
      const reports = await reportService.getAllReports();
      return res.status(200).json(reports);
    } catch (error) {
      const status = error.statusCode || 500;
      return res.status(status).json({ message: error.message || 'Internal Server Error' });
    }
  }

  static async getById(req, res) {
    try {
      const { id } = req.params;
      const report = await reportService.getReportById(id);
      return res.status(200).json(report);
    } catch (error) {
      const status = error.statusCode || 500;
      return res.status(status).json({ message: error.message || 'Internal Server Error' });
    }
  }

  static async generate(req, res) {
    try {
      const { title } = req.body || {};
      const newReport = await reportService.createReport(title);
      // RMM Lvl 2 for successful creation
      return res.status(201).json(newReport);
    } catch (error) {
      const status = error.statusCode || 500;
      return res.status(status).json({ message: error.message || 'Internal Server Error' });
    }
  }

  static async delete(req, res) {
    try {
      const { id } = req.params;
      await reportService.deleteReport(id);
      // RMM Lvl 2 for successful deletion w/o body
      return res.status(204).send();
    } catch (error) {
      const status = error.statusCode || 500;
      return res.status(status).json({ message: error.message || 'Internal Server Error' });
    }
  }
}

module.exports = ReportController;
