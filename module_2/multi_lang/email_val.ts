// Prompt: "Function to validate email format and check if exists in database with type safety"
// Copilot will suggest:
// - interface definitions for User
// - typed return values
// - strict null checks
interface User {
    id: number;
    email: string;
}

async function validateAndCheckEmail(email: string): Promise<boolean> {
    // Simple regex for email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        return false; // Invalid email format
    }

    // Simulated database check
    const userDatabase: User[] = [
        { id: 1, email: "user@example.com" },
        { id: 2, email: "admin@test.com" }
    ];

    // Check if email exists in database
    const userExists = userDatabase.some(user => user.email === email);
    return userExists;
}