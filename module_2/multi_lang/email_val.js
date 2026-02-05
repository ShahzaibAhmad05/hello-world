// Prompt: "Function to validate email format and check if user exists in database using Mongoose"
// Copilot will suggest:
// - regex pattern for validation
// - async/await for database query
// - Promise-based error handling
const User = require('./models/User');

async function validateAndCheckEmail(email) {
    // Regular expression for basic email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    // Validate email format
    if (!emailRegex.test(email)) {
        throw new Error('Invalid email format');
    }

    // Check if user exists in the database
    const user = await User.findOne({ email: email });
    if (!user) {
        throw new Error('User does not exist');
    }
    return true; // Email is valid and user exists
}