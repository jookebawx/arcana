const express = require('express');
const path = require('path');
const app = express();
const port = 3000;

// Serve static files from the "public" directory
app.use(express.static(path.join(__dirname, 'public')));

// Middleware to parse JSON data
app.use(express.json());

let loggedInUser = null;

// Set login.html as the landing page
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'login.html'));
});

// Route to serve the homepage
app.get('/homepage', (req, res) => {
  if (loggedInUser) {
    res.sendFile(path.join(__dirname, 'public', 'homepage.html'));
  } else {
    res.redirect('/');
  }
});

// Route to serve the wallet page
app.get('/wallet', (req, res) => {
  if (loggedInUser) {
    res.sendFile(path.join(__dirname, 'public', 'wallet.html'));
  } else {
    res.redirect('/');
  }
});

// Login route
app.post('/login', (req, res) => {
  const { metamaskAccount } = req.body;
  // Mock authentication process
  loggedInUser = { name: 'User', email: `${metamaskAccount}@crypto.com` };
  res.json({ success: true, message: 'Logged in successfully!' });
});

// Logout route
app.get('/logout', (req, res) => {
  loggedInUser = null;
  res.redirect('/');
});

// Start the server
app.listen(port, () => {
  console.log(`App listening at http://localhost:${port}`);
});
