document.addEventListener('DOMContentLoaded', () => {
    const metamaskAddressElement = document.getElementById('metamaskAddress');
    
    // Function to get the value of a cookie by name
    function getCookie(name) {
      const value = `; ${document.cookie}`;
      const parts = value.split(`; ${name}=`);
      if (parts.length === 2) return parts.pop().split(';').shift();
    }

    // Read the MetaMask address from the cookie
    const metamaskAddress = getCookie('metamaskAccount');
    if (metamaskAddress) {
      metamaskAddressElement.textContent = metamaskAddress;
    } else {
      metamaskAddressElement.textContent = 'No account found';
    }
  });