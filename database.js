// This file stores user credentials.
// IMPORTANT: This is for demonstration purposes only and is NOT secure.
// In a real application, passwords should never be stored in plaintext.
// They should be hashed and salted.

const users = [
  { username: 'bill', password: 'password' },   // Simple 8-char password
  { username: 'bryan', password: 'bryan123' },  // Simple 8-char password
  { username: 'matt', password: 'mattpass' },    // Simple 8-char password
  { username: 'john', password: 'johnlego' }    // Simple 8-char password
];

// Function to get users (optional, but good practice to encapsulate data)
function getUsers() {
  return users;
}

// If using Node.js modules, you might export the users array or the function
// For example:
// module.exports = users;
// or
// module.exports = { getUsers };

// For browser environments, this variable will be globally accessible if the script is included.
// Or you can attach it to the window object, e.g., window.appUsers = users;
