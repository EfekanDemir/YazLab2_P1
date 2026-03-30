const IReportRepository = require('./IReportRepository');
const Report = require('../models/Report');

class MongoReportRepository extends IReportRepository {
  constructor() {
    super();
  }

  async findAll() {
    return await Report.find({});
  }

  async findById(id) {
    return await Report.findById(id);
  }

  async create(reportData) {
    const report = new Report(reportData);
    return await report.save();
  }

  async delete(id) {
    return await Report.findByIdAndDelete(id);
  }
}

module.exports = MongoReportRepository;
