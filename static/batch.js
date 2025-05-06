document.getElementById('batchForm').addEventListener('submit', function(e) {
  const sourceFolder = document.getElementById('sourceFolder').value.trim();
  if (!sourceFolder) {
    e.preventDefault();
    alert('请输入源文件夹路径！');
    return;
  }

  const selectedFiles = Array.from(document.querySelectorAll('input[name="filesToCopy"]:checked'))
    .map(checkbox => checkbox.value);
  document.getElementById('selectedFiles').value = selectedFiles.join(',');

  const button = document.querySelector('#batchForm button[type="submit"]');
  button.textContent = '复制中...';
  button.disabled = true;
});

function listFiles() {
  const sourceFolder = document.getElementById('sourceFolder').value.trim();
  if (!sourceFolder) {
    alert('请输入源文件夹路径！');
    return;
  }

  fetch('/list_files', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: `sourceFolder=${encodeURIComponent(sourceFolder)}`
  })
  .then(response => response.json())
  .then(data => {
    if (data.error) {
      alert(data.error);
    } else {
      const fileList = document.getElementById('fileList');
      const fileListContainer = document.getElementById('fileListContainer');
      fileList.innerHTML = '';
      data.files.forEach(file => {
        const li = document.createElement('li');
        li.className = 'flex items-center';
        li.innerHTML = `
          <input type="checkbox" name="filesToCopy" value="${file}" class="mr-2">
          <span>${file}</span>
        `;
        fileList.appendChild(li);
      });
      fileListContainer.style.display = 'block';
    }
  })
  .catch(error => alert(`读取文件失败：${error}`));
}