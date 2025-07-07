document.getElementById('download-form').addEventListener('submit', async function(e) {
  e.preventDefault();
  
  const url = document.getElementById('url').value.trim();
  const button = document.querySelector('button[type="submit"]');
  const buttonText = document.getElementById('button-text');
  const loadingSpinner = document.getElementById('loading-spinner');
  
  // Validate URL
  if (!url) {
    showErrorMessage('Please enter a valid URL');
    return;
  }
  
  // Show loading state
  button.disabled = true;
  buttonText.classList.add('hidden');
  loadingSpinner.classList.remove('hidden');
  button.classList.add('opacity-75');
  
  try {
    // Use the correct API endpoint for Vercel
    const apiUrl = '/api/download';
      
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify({ url })
    });
    
    console.log('Response status:', response.status);
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error('API Error:', errorText);
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    console.log('API Response:', data);
    
    if (data.success && data.download_url) {
      // Success - show download info and trigger download
      showSuccessMessage(`Downloading ${data.title} from ${data.platform}...`);
      
      // Create a temporary link to trigger download
      const link = document.createElement('a');
      link.href = data.download_url;
      link.download = `${data.platform}_video.mp4`;
      link.target = '_blank';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      // Show success message
      setTimeout(() => {
        showSuccessMessage('Download completed! Check your downloads folder.');
      }, 2000);
      
    } else {
      // Error
      showErrorMessage(data.error || data.detail || 'Download failed. Please try again.');
    }
  } catch (error) {
    console.error('Download error:', error);
    if (error.message.includes('HTTP error')) {
      showErrorMessage('Server error. Please try again later.');
    } else if (error.message.includes('Failed to fetch')) {
      showErrorMessage('Network error. Please check your connection and try again.');
    } else {
      showErrorMessage('An unexpected error occurred. Please try again.');
    }
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
  }, 5000);
}

function showErrorMessage(message) {
  const notification = document.createElement('div');
  notification.className = 'fixed top-4 right-4 bg-red-600 text-white px-6 py-3 rounded-lg shadow-lg z-50 animate-fadeInUp';
  notification.textContent = message;
  document.body.appendChild(notification);
  
  setTimeout(() => {
    notification.remove();
  }, 7000);
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
  
  // Add hover effects to platform badges
  const platformBadges = document.querySelectorAll('.flex.flex-wrap > span');
  platformBadges.forEach(badge => {
    badge.addEventListener('mouseenter', function() {
      this.style.transform = 'scale(1.05)';
      this.style.transition = 'transform 0.2s ease';
    });
    
    badge.addEventListener('mouseleave', function() {
      this.style.transform = 'scale(1)';
    });
  });
  
  // Test API connection
  testApiConnection();
});

async function testApiConnection() {
  try {
    const apiUrl = window.location.hostname === 'localhost' 
      ? 'http://localhost:8000/health'
      : '/api/health';
      
    const response = await fetch(apiUrl);
    if (response.ok) {
      console.log('API connection successful');
    }
  } catch (error) {
    console.log('API connection test failed (this is normal for local development)');
  }
} 