const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');

class AuthService {
  /**
   * We inject the repository so the service isn't hardcoded 
   * to a specific DB implementation.
   */
  constructor(userRepository) {
    this.userRepository = userRepository;
    this.jwtSecret = process.env.JWT_SECRET || 'super_secret_fallback_key';
  }

  async register(username, password) {
    // Check if user already exists
    const existingUser = await this.userRepository.findByUsername(username);
    if (existingUser) {
      const error = new Error('User already exists');
      error.statusCode = 409; 
      throw error;
    }

    // Hash password
    const salt = await bcrypt.genSalt(10);
    const hashedPassword = await bcrypt.hash(password, salt);

    // Create user in DB
    const newUser = await this.userRepository.create({
      username,
      password: hashedPassword,
      tokens: []
    });

    return { id: newUser._id, username: newUser.username };
  }

  async login(username, password) {
    const user = await this.userRepository.findByUsername(username);
    if (!user) {
      const error = new Error('Invalid credentials');
      error.statusCode = 401;
      throw error;
    }

    // Verify password
    const isMatch = await bcrypt.compare(password, user.password);
    if (!isMatch) {
      const error = new Error('Invalid credentials');
      error.statusCode = 401;
      throw error;
    }

    // Generate JWT
    const token = jwt.sign(
      { id: user._id, username: user.username },
      this.jwtSecret,
      { expiresIn: '1d' }
    );

    // Save token for multi-device login feature
    await this.userRepository.saveToken(user._id, token);

    return {
      token,
      user: { id: user._id, username: user.username }
    };
  }

  async logout(userId, token) {
    // Remove the specific token from the user's active tokens list
    await this.userRepository.removeToken(userId, token);
    return true;
  }
}

module.exports = AuthService;
