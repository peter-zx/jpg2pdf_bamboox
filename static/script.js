document.getElementById('jpgFiles').addEventListener('change', function(e) {
  const files = e.target.files;
  const fileList = document.getElementById('fileListSingle');
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

document.getElementById('fileListSingle').addEventListener('click', function(e) {
  if (e.target.classList.contains('move-up') || e.target.classList.contains('move-down')) {
    const li = e.target.closest('.file-item');
    const fileList = document.getElementById('fileListSingle');
    const index = Array.from(fileList.children).indexOf(li);

    if (e.target.classList.contains('move-up') && index > 0) {
      fileList.insertBefore(li, fileList.children[index - 1]);
    } else if (e.target.classList.contains('move-down') && index < fileList.children.length - 1) {
      fileList.insertBefore(fileList.children[index + 1], li);
    }

    Array.from(fileList.children).forEach((item, i) => {
      item.querySelector('.move-up').disabled = i === 0;
      item.querySelector('.move-down').disabled = i === fileList.children.length - 1;
    });

    updateFileOrder();
  }
});

function updateFileOrder() {
  const fileList = document.getElementById('fileListSingle');
  const fileOrder = Array.from(fileList.children).map(item => item.dataset.filename);
  document.getElementById('fileOrder').value = fileOrder.join(',');
}

document.getElementById('singleMode').addEventListener('change', function() {
  document.getElementById('singleModeFields').style.display = 'block';
  document.getElementById('multiModeFields').style.display = 'none';
  document.getElementById('subfolderListContainer').style.display = 'none';
});

document.getElementById('multiMode').addEventListener('change', function() {
  document.getElementById('singleModeFields').style.display = 'none';
  document.getElementById('multiModeFields').style.display = 'block';
});

function listSubfolders() {
  const parentFolder = document.getElementById('parentFolder').value.trim();
  if (!parentFolder) {
    alert('请输入一级文件夹路径！');
    return;
  }

  fetch('/list_subfolders', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: `parentFolder=${encodeURIComponent(parentFolder)}`
  })
  .then(response => response.json())
  .then(data => {
    if (data.error) {
      alert(data.error);
    } else {
      const subfolderList = document.getElementById('subfolderList');
      const subfolderListContainer = document.getElementById('subfolderListContainer');
      subfolderList.innerHTML = '';
      data.subfolders.forEach(subfolder => {
        const li = document.createElement('li');
        li.className = 'flex items-center';
        li.innerHTML = `
          <input type="checkbox" name="subfoldersToConvert" value="${subfolder}" class="mr-2">
          <span>${subfolder}</span>
        `;
        subfolderList.appendChild(li);
      });
      subfolderListContainer.style.display = 'block';
    }
  })
  .catch(error => alert(`读取子文件夹失败：${error}`));
}

function processForm() {
  const form = document.getElementById('uploadForm');
  const formData = new FormData(form);
  const submitButton = document.getElementById('submitButton');
  const progressContainer = document.getElementById('progressContainer');
  const progressFill = document.getElementById('progressFill');
  const progressText = document.getElementById('progressText');
  const completedText = document.getElementById('completedText');
  const errorText = document.getElementById('errorText');

  submitButton.disabled = true;
  submitButton.textContent = '处理中...';
  progressContainer.style.display = 'block';
  progressFill.style.width = '0%';
  progressText.style.display = 'none';
  completedText.style.display = 'none';
  errorText.style.display = 'none';

  if (document.getElementById('multiMode').checked) {
    const selectedSubfolders = Array.from(document.querySelectorAll('input[name="subfoldersToConvert"]:checked'))
      .map(checkbox => checkbox.value);
    formData.set('selectedSubfolders', selectedSubfolders.join(','));

    const total = selectedSubfolders.length;
    let processed = 0;

    const interval = setInterval(() => {
      processed++;
      const percentage = (processed / total) * 100;
      progressFill.style.width = `${percentage}%`;
      if (processed >= total) clearInterval(interval);
    }, 500);
  } else {
    progressFill.style.width = '100%';
  }

  fetch('/process_single', {
    method: 'POST',
    body: formData
  })
  .then(response => response.json())
  .then(data => {
    submitButton.disabled = false;
    submitButton.textContent = '合并并保存PDF';

    if (data.error) {
      errorText.textContent = data.error;
      errorText.style.display = 'block';
    } else {
      if (data.progress) {
        progressText.textContent = data.progress;
        progressText.style.display = 'block';
      }
      if (data.completed) {
        completedText.textContent = data.completed;
        completedText.style.display = 'block';
      }
      if (data.processed_folders && data.processed_folders.length > 0) {
        completedText.textContent += `\n已为以下子文件夹生成PDF：${data.processed_folders.join(', ')}`;
      }
    }
  })
  .catch(error => {
    submitButton.disabled = false;
    submitButton.textContent = '合并并保存PDF';
    errorText.textContent = `处理失败：${error}`;
    errorText.style.display = 'block';
  });
}