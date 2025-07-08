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
    showSuccessMessage('Fetching available YouTube qualities...');
    try {
      const res = await fetch(`/api/download/qualities?url=${encodeURIComponent(url)}`);
      const data = await res.json();
      if (data.success && Array.isArray(data.qualities)) {
        // Only show qualities with audio
        youtubeQualities = data.qualities.filter(q => q.has_audio);
        if (youtubeQualities.length === 0) {
          showErrorMessage('No downloadable YouTube qualities with audio found.');
          showQualityDropdown(false);
          return;
        }
        // Populate dropdown
        const select = document.getElementById('quality-dropdown');
        select.innerHTML = '';
        youtubeQualities.forEach((q, i) => {
          const opt = document.createElement('option');
          opt.value = i;
          opt.textContent = `${q.quality} (${q.size})`;
          select.appendChild(opt);
        });
        selectedQualityIndex = 0;
        select.value = 0;
        showQualityDropdown(true);
      } else {
        showErrorMessage(data.error || 'Could not fetch YouTube qualities.');
        showQualityDropdown(false);
      }
    } catch (err) {
      showErrorMessage('Failed to fetch YouTube qualities.');
      showQualityDropdown(false);
    }
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
      // Success - show download info and open in new tab
      showSuccessMessage(`Ready: ${data.title} from ${data.platform}. Click the link to download.`);
      window.open(data.download_url, '_blank');
      // Do not auto-download, just open the link
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