document.getElementById('batchForm').addEventListener('submit', function() {
    const button = document.querySelector('button[type="submit"]');
    button.textContent = '处理中...';
    button.disabled = true;
  });