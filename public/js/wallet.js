// Function to initialize Web3 and fetch account info
async function init() {
    if (window.ethereum) {
      try {
        // Initialize Web3 provider
        const web3 = new Web3(window.ethereum);
  
        // Request account access
        const accounts = await web3.eth.getAccounts();
        if (accounts.length > 0) {
          const account = accounts[0];
          document.getElementById('metamaskAddress').textContent = `${account}`;;
          document.getElementById('account').textContent = `Account: ${account}`;
            
          // Get balance and convert from Wei
          const balanceWei = await web3.eth.getBalance(account);
          const balanceEth = web3.utils.fromWei(balanceWei, 'ether');
          document.getElementById('balance').textContent = `Balance: ${balanceEth} ETH`;
        } else {
          document.getElementById('account').textContent = 'No account connected';
        }
      } catch (error) {
        console.error('Error retrieving account information:', error);
        alert('Error retrieving account information');
      }
    } else {
      alert('MetaMask is not installed');
    }
  }
  
  // Initialize the wallet information on page load
  window.addEventListener('load', init);
  