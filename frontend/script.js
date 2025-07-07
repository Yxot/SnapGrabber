document.getElementById('download-form').addEventListener('submit', async function(e) {
  e.preventDefault();
  const url = document.getElementById('url').value;
  const response = await fetch('http://localhost:8000/download', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url })
  });
  const data = await response.json();
  if (data.download_url) {
    window.location.href = data.download_url;
  } else {
    alert(data.error || 'Download failed.');
  }
}); 