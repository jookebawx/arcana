async function connectMetaMask() {
  if (typeof window.ethereum !== 'undefined') {
    try {
      const accounts = await ethereum.request({ method: 'eth_requestAccounts' });
      const account = accounts[0];

      // Set a cookie with the MetaMask account
      document.cookie = `metamaskAccount=${encodeURIComponent(account)}; path=/`;

      // Optionally, send the account to the server for authentication
      const response = await fetch('/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ metamaskAccount: account })
      });

      const data = await response.json();
      if (data.success) {
        window.location.href = '/homepage'; // Redirect on success
      } else {
        alert('Login failed');
      }
    } catch (error) {
      console.error('Error connecting MetaMask:', error);
      alert('Error connecting to MetaMask');
    }
  } else {
    alert('MetaMask is not installed');
  }
}
