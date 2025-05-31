// Default users array
const defaultUsers = [
    { username: 'bill', password: 'password', name: 'Bill Lego' },
    { username: 'bryan', password: 'bryan123', name: 'Bryan Brick' },
    { username: 'matt', password: 'mattpass', name: 'Matt Plate' },
    { username: 'john', password: 'johnlego', name: 'John Stud' }
];

// Declare users array with let to allow modification
let users;

// Try to load users from localStorage
const storedUsers = localStorage.getItem('usersDB');

if (storedUsers) {
    try {
        users = JSON.parse(storedUsers);
        // Optional: Add a check to ensure parsed data is an array
        if (!Array.isArray(users)) {
            console.warn('Stored usersDB was not an array, falling back to default users.');
            users = [...defaultUsers];
        } else if (users.length === 0 && defaultUsers.length > 0) {
            // If localStorage had an empty array but defaults exist, re-initialize with defaults
            // This handles a case where localStorage might have been cleared or set to [] erroneously
            // and we want to ensure default users are present for a "first run" experience.
            console.warn('Stored usersDB was empty, re-initializing with default users.');
            users = [...defaultUsers];
        }
    } catch (e) {
        console.error('Error parsing usersDB from localStorage, falling back to default users:', e);
        users = [...defaultUsers]; // Use a copy to avoid modifying defaultUsers directly
    }
} else {
    // If no users in localStorage, initialize with default users
    users = [...defaultUsers]; // Use a copy
}

// Function to save users to localStorage (can be called by registration script)
function saveUsersToLocalStorage() {
    try {
        localStorage.setItem('usersDB', JSON.stringify(users));
    } catch (e) {
        console.error('Error saving users to localStorage:', e);
    }
}

// Immediately save the initialized or loaded users array to localStorage
// This ensures that if it was the first load, default users are stored.
// If users were loaded from localStorage, it re-saves them (which is fine).
saveUsersToLocalStorage();

// Optional: A function to add a user, which also saves.
// This can be used by the registration script.
function addUser(user) {
    if (users.find(u => u.username === user.username)) {
        console.warn(`User ${user.username} already exists.`);
        return false; // Indicate failure
    }
    users.push(user);
    saveUsersToLocalStorage();
    return true; // Indicate success
}

/*
    Important:
    The `users` array is now the single source of truth during the session,
    loaded from localStorage or defaults.
    The registration page will need to call `addUser(newUserObject)` or directly
    manipulate the `users` array and then call `saveUsersToLocalStorage()`.
    The login page will use the `users` array as is.
*/
