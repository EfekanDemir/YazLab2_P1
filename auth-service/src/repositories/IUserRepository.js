/**
 * Base Abstract Class defining the UserRepository Interface.
 * JavaScript does not have strict interfaces, so we implement an abstract class
 * that throws an error if methods are not implemented by the child.
 */
class IUserRepository {
  constructor() {
    if (this.constructor === IUserRepository) {
      throw new Error("Abstract classes can't be instantiated.");
    }
  }

  async findByUsername(username) {
    throw new Error("Method 'findByUsername()' must be implemented.");
  }

  async create(userObj) {
    throw new Error("Method 'create()' must be implemented.");
  }

  async saveToken(userId, token) {
    throw new Error("Method 'saveToken()' must be implemented.");
  }

  async removeToken(userId, token) {
    throw new Error("Method 'removeToken()' must be implemented.");
  }
}

module.exports = IUserRepository;
