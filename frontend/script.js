let youtubeQualities = [];
let selectedQualityIndex = null;

// Helper: Check if URL is YouTube
function isYouTubeUrl(url) {
  return url.includes('youtube.com') || url.includes('youtu.be');
}

// Helper: Show/hide quality dropdown
function showQualityDropdown(show) {
  const dropdown = document.getElementById('quality-dropdown-container');
  if (dropdown) dropdown.style.display = show ? 'block' : 'none';
}

// Listen for input changes to fetch YouTube qualities
const urlInput = document.getElementById('url');
urlInput.addEventListener('change', async function() {
  const url = urlInput.value.trim();
  if (isYouTubeUrl(url)) {
    // For now, just hide the dropdown since quality fetching isn't working
    showQualityDropdown(false);
  } else {
    showQualityDropdown(false);
  }
});

// Listen for dropdown change
function setupQualityDropdownListener() {
  const select = document.getElementById('quality-dropdown');
  if (select) {
    select.addEventListener('change', function() {
      selectedQualityIndex = parseInt(this.value, 10);
    });
  }
}

document.addEventListener('DOMContentLoaded', setupQualityDropdownListener);

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
  
  // Validate URL format
  if (!url.match(/^https?:\/\//)) {
    showErrorMessage('Please enter a valid URL starting with http:// or https://');
    return;
  }
  
  // Show loading state
  button.disabled = true;
  buttonText.classList.add('hidden');
  loadingSpinner.classList.remove('hidden');
  button.classList.add('opacity-75');
  
  try {
    let body = { url };
    // If YouTube and quality selected, add quality_index
    if (isYouTubeUrl(url) && youtubeQualities.length > 0 && selectedQualityIndex !== null) {
      body.quality_index = selectedQualityIndex;
    }
    const apiUrl = '/api/download';
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify(body)
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
      link.download = `${data.platform}_${Date.now()}.mp4`;
      link.target = '_blank';
      link.rel = 'noopener noreferrer';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      // Show success message
      setTimeout(() => {
        showSuccessMessage('Download completed! Check your downloads folder.');
      }, 2000);
      
      // Clear the form
      document.getElementById('url').value = '';
      showQualityDropdown(false);
    } else {
      // Error
      const errorMessage = data.error || data.detail || 'Download failed. Please try again.';
      showErrorMessage(errorMessage);
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
  notification.className = 'fixed top-4 right-4 bg-green-600 text-white px-6 py-3 rounded-lg shadow-lg z-50 animate-fadeInUp max-w-sm';
  notification.innerHTML = `
    <div class="flex items-center">
      <span class="mr-2">✅</span>
      <span>${message}</span>
    </div>
  `;
  document.body.appendChild(notification);
  
  setTimeout(() => {
    notification.style.opacity = '0';
    notification.style.transform = 'translateX(100%)';
    setTimeout(() => notification.remove(), 300);
  }, 5000);
}

function showErrorMessage(message) {
  const notification = document.createElement('div');
  notification.className = 'fixed top-4 right-4 bg-red-600 text-white px-6 py-3 rounded-lg shadow-lg z-50 animate-fadeInUp max-w-sm';
  notification.innerHTML = `
    <div class="flex items-center">
      <span class="mr-2">❌</span>
      <span>${message}</span>
    </div>
  `;
  document.body.appendChild(notification);
  
  setTimeout(() => {
    notification.style.opacity = '0';
    notification.style.transform = 'translateX(100%)';
    setTimeout(() => notification.remove(), 300);
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
  
  // Test API connection on load
  testApiConnection();
  
  // Add URL validation on input
  const urlInput = document.getElementById('url');
  urlInput.addEventListener('input', function() {
    const url = this.value.trim();
    if (url && !url.match(/^https?:\/\//)) {
      this.classList.add('border-red-500');
    } else {
      this.classList.remove('border-red-500');
    }
  });
});

async function testApiConnection() {
  try {
    const apiUrl = '/api/download';
    const response = await fetch(apiUrl, { method: 'GET' });
    if (response.ok) {
      const data = await response.json();
      console.log('API connection successful:', data);
    }
  } catch (error) {
    console.log('API connection test failed (this is normal for local development)');
  }
} 