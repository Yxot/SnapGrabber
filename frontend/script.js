document.getElementById('download-form').addEventListener('submit', async function(e) {
  e.preventDefault();
  
  const url = document.getElementById('url').value;
  const button = document.querySelector('button[type="submit"]');
  const buttonText = document.getElementById('button-text');
  const loadingSpinner = document.getElementById('loading-spinner');
  
  // Show loading state
  button.disabled = true;
  buttonText.classList.add('hidden');
  loadingSpinner.classList.remove('hidden');
  button.classList.add('opacity-75');
  
  try {
    const response = await fetch('http://localhost:8000/download', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url })
    });
    
    const data = await response.json();
    
    if (data.download_url) {
      // Success - trigger download
      showSuccessMessage('Download starting...');
      setTimeout(() => {
        window.location.href = data.download_url;
      }, 1000);
    } else {
      // Error
      showErrorMessage(data.error || 'Download failed. Please try again.');
    }
  } catch (error) {
    console.error('Download error:', error);
    showErrorMessage('Network error. Please check your connection and try again.');
  } finally {
    // Reset button state
    button.disabled = false;
    buttonText.classList.remove('hidden');
    loadingSpinner.classList.add('hidden');
    button.classList.remove('opacity-75');
  }
});

function showSuccessMessage(message) {
  const notification = document.createElement('div');
  notification.className = 'fixed top-4 right-4 bg-green-600 text-white px-6 py-3 rounded-lg shadow-lg z-50 animate-fadeInUp';
  notification.textContent = message;
  document.body.appendChild(notification);
  
  setTimeout(() => {
    notification.remove();
  }, 3000);
}

function showErrorMessage(message) {
  const notification = document.createElement('div');
  notification.className = 'fixed top-4 right-4 bg-red-600 text-white px-6 py-3 rounded-lg shadow-lg z-50 animate-fadeInUp';
  notification.textContent = message;
  document.body.appendChild(notification);
  
  setTimeout(() => {
    notification.remove();
  }, 5000);
}

// Add some interactive animations
document.addEventListener('DOMContentLoaded', function() {
  // Add hover effects to feature cards
  const featureCards = document.querySelectorAll('.grid > div');
  featureCards.forEach(card => {
    card.addEventListener('mouseenter', function() {
      this.style.transform = 'translateY(-5px)';
      this.style.transition = 'transform 0.2s ease';
    });
    
    card.addEventListener('mouseleave', function() {
      this.style.transform = 'translateY(0)';
    });
  });
}); 