document.getElementById('batchForm').addEventListener('submit', function() {
  const button = document.querySelector('#batchForm button[type="submit"]');
  button.textContent = '处理中...';
  button.disabled = true;
});

function mergeFolder(name) {
  const folderInput = document.getElementById(`folder_${name}`);
  const folderPath = folderInput.value.trim();
  if (!folderPath) {
    alert('请输入文件夹路径！');
    return;
  }

  fetch('/batch/merge', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: `personFolder=${encodeURIComponent(folderPath)}&name=${encodeURIComponent(name)}`
  })
  .then(response => response.json())
  .then(data => {
    if (data.error) {
      alert(data.error);
    } else {
      alert(data.message);
      folderInput.value = '';
    }
  })
  .catch(error => alert(`请求失败：${error}`));
}