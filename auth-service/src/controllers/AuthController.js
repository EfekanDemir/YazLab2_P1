const AuthService = require('../services/AuthService');
const MongoUserRepository = require('../repositories/MongoUserRepository');

// Instantiate dependencies
const userRepository = new MongoUserRepository();
const authService = new AuthService(userRepository);

class AuthController {
  
  static async register(req, res) {
    try {
      const { username, password } = req.body;
      
      if (!username || !password) {
        return res.status(400).json({ message: 'Username and password are required' });
      }

      const user = await authService.register(username, password);
      // RMM Level 2 -> 201 Created
      return res.status(201).json({ message: 'User registered successfully', user });
    } catch (error) {
      const status = error.statusCode || 500;
      return res.status(status).json({ message: error.message || 'Internal Server Error' });
    }
  }

  static async login(req, res) {
    try {
      const { username, password } = req.body;

      if (!username || !password) {
        return res.status(400).json({ message: 'Username and password are required' });
      }

      const loginResult = await authService.login(username, password);
      return res.status(200).json(loginResult);
    } catch (error) {
      const status = error.statusCode || 500;
      return res.status(status).json({ message: error.message || 'Internal Server Error' });
    }
  }

  static async logout(req, res) {
    try {
      // In a real scenario, you'd extract the userId and token from a logged-in middleware (req.user).
      // Here, assuming client sends the token in headers or body to log out.
      // If token is in Authorization: Bearer <token>
      const authHeader = req.headers.authorization;
      if (!authHeader || !authHeader.startsWith('Bearer ')) {
         return res.status(400).json({ message: 'Token is required for logout' });
      }
      
      const token = authHeader.split(' ')[1];
      const jwt = require('jsonwebtoken');
      
      let decoded;
      try {
        decoded = jwt.decode(token);
      } catch (err) {
        return res.status(400).json({ message: 'Invalid token format' });
      }

      if (!decoded || !decoded.id) {
         return res.status(400).json({ message: 'Invalid token payload' });
      }

      await authService.logout(decoded.id, token);
      return res.status(200).json({ message: 'Logged out successfully' });
    } catch (error) {
      const status = error.statusCode || 500;
      return res.status(status).json({ message: error.message || 'Internal Server Error' });
    }
  }
}

module.exports = AuthController;
