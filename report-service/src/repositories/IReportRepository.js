class IReportRepository {
  constructor() {
    if (this.constructor === IReportRepository) {
      throw new Error("Abstract classes can't be instantiated.");
    }
  }

  async findAll() {
    throw new Error("Method 'findAll()' must be implemented.");
  }

  async findById(id) {
    throw new Error("Method 'findById()' must be implemented.");
  }

  async create(reportData) {
    throw new Error("Method 'create()' must be implemented.");
  }

  async delete(id) {
    throw new Error("Method 'delete()' must be implemented.");
  }
}

module.exports = IReportRepository;
