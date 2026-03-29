const IUserRepository = require('./IUserRepository');
const User = require('../models/User');

class MongoUserRepository extends IUserRepository {
  constructor() {
    super();
  }

  async findByUsername(username) {
    return await User.findOne({ username });
  }

  async create(userObj) {
    const user = new User(userObj);
    return await user.save();
  }

  async saveToken(userId, token) {
    return await User.findByIdAndUpdate(
      userId,
      { $push: { tokens: token } },
      { new: true }
    );
  }

  async removeToken(userId, token) {
    return await User.findByIdAndUpdate(
      userId,
      { $pull: { tokens: token } },
      { new: true }
    );
  }
}

module.exports = MongoUserRepository;
