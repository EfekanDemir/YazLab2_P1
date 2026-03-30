const express = require('express');
const ReportController = require('../controllers/ReportController');
const internalGuard = require('../middleware/internalGuard');

const router = express.Router();

// Her route'a internal guard ekliyoruz
router.use(internalGuard);

router.get('/', ReportController.getAll);
router.get('/:id', ReportController.getById);
router.post('/generate', ReportController.generate);
router.delete('/:id', ReportController.delete);

module.exports = router;
