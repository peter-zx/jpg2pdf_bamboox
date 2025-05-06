document.getElementById('jpgFiles').addEventListener('change', function(e) {
  const files = e.target.files;
  const fileList = document.getElementById('fileList');
  fileList.innerHTML = '';

  Array.from(files).forEach((file, index) => {
    if (file.type.match('image/jpeg')) {
      const li = document.createElement('li');
      li.className = 'file-item';
      li.dataset.filename = file.name;
      li.innerHTML = `
        <span>${file.name}</span>
        <div>
          <button type="button" class="move-up" ${index === 0 ? 'disabled' : ''}>↑</button>
          <button type="button" class="move-down" ${index === files.length - 1 ? 'disabled' : ''}>↓</button>
        </div>
      `;
      fileList.appendChild(li);
    }
  });

  updateFileOrder();
});

// 上下移动事件
document.getElementById('fileList').addEventListener('click', function(e) {
  if (e.target.classList.contains('move-up') || e.target.classList.contains('move-down')) {
    const li = e.target.closest('.file-item');
    const fileList = document.getElementById('fileList');
    const index = Array.from(fileList.children).indexOf(li);

    if (e.target.classList.contains('move-up') && index > 0) {
      fileList.insertBefore(li, fileList.children[index - 1]);
    } else if (e.target.classList.contains('move-down') && index < fileList.children.length - 1) {
      fileList.insertBefore(fileList.children[index + 1], li);
    }

    // 更新按钮状态
    Array.from(fileList.children).forEach((item, i) => {
      item.querySelector('.move-up').disabled = i === 0;
      item.querySelector('.move-down').disabled = i === fileList.children.length - 1;
    });

    updateFileOrder();
  }
});

function updateFileOrder() {
  const fileList = document.getElementById('fileList');
  const fileOrder = Array.from(fileList.children).map(item => item.dataset.filename);
  document.getElementById('fileOrder').value = fileOrder.join(',');
}

// 提交前更新文件顺序
document.getElementById('uploadForm').addEventListener('submit', () => {
  updateFileOrder();
});