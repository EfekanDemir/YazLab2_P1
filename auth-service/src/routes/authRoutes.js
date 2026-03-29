const express = require('express');
const AuthController = require('../controllers/AuthController');
const internalGuard = require('../middleware/internalGuard');

const router = express.Router();

// Apply internal guard to all auth routes to prevent direct access bypass
router.use(internalGuard);

router.post('/register', AuthController.register);
router.post('/login', AuthController.login);
router.post('/logout', AuthController.logout);

module.exports = router;
