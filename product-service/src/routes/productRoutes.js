const express = require('express');
const ProductController = require('../controllers/ProductController');
const internalGuard = require('../middleware/internalGuard');

const router = express.Router();

// Apply internal guard to all product routes to prevent direct access bypass
router.use(internalGuard);

router.get('/', ProductController.getAll);
router.get('/:id', ProductController.getById);
router.post('/', ProductController.create);
router.put('/:id', ProductController.update);
router.delete('/:id', ProductController.delete);

module.exports = router;
