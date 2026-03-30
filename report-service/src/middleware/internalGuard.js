/**
 * Middleware: internalGuard
 * Verifies that the request comes from an internal source (e.g. API Gateway)
 * Checks for the x-internal-request header.
 */
const internalGuard = (req, res, next) => {
  const isInternal = req.headers['x-internal-request'];
  
  if (isInternal !== 'true') {
    return res.status(403).json({ 
      message: 'Forbidden. Direct access to this service is not allowed.' 
    });
  }
  
  next();
};

module.exports = internalGuard;
