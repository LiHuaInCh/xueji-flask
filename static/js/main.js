/* ===================== 学迹 · 前端交互 ===================== */

// 收藏 / 取消收藏：用 fetch 发 AJAX 请求，局部刷新按钮，不整页跳转
document.addEventListener('DOMContentLoaded', function () {
  var btn = document.getElementById('fav-btn');
  if (!btn) { return; }

  btn.addEventListener('click', function () {
    btn.disabled = true;
    fetch(btn.dataset.url, {
      method: 'POST',
      headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
      .then(function (res) {
        // 未登录时 Flask-Login 会返回登录页，这里给出提示
        if (res.redirected || res.status === 401) {
          alert('请先登录再收藏');
          window.location.href = '/auth/login';
          return null;
        }
        return res.json();
      })
      .then(function (data) {
        if (!data) { return; }
        btn.innerText = data.favorited ? '❤️ 已收藏' : '🤍 收藏';
        btn.classList.toggle('btn-danger', data.favorited);
        btn.classList.toggle('btn-outline-danger', !data.favorited);
      })
      .catch(function () { alert('操作失败，请稍后重试'); })
      .finally(function () { btn.disabled = false; });
  });
});

// 上传文件大小前端预检（和 config.py 里的 MAX_CONTENT_LENGTH 保持一致）
document.addEventListener('change', function (e) {
  if (e.target && e.target.type === 'file') {
    var max = 8 * 1024 * 1024;
    if (e.target.files[0] && e.target.files[0].size > max) {
      alert('文件超过 8MB，请压缩后再上传');
      e.target.value = '';
    }
  }
});
