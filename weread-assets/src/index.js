addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
  if (request.method !== 'POST') {
    return new Response('Expecting a POST request', { status: 400 })
  }

  const data = await request.json();
  const contentBase64 = data.file;
  const filename = data.filename;
  const folder = data.folder || 'images'; // 默认文件夹为空，如果没有提供文件夹参数

  if (!contentBase64) {
    return new Response('No file content provided', { status: 400 })
  }

  const owner = 'qweruqwio';
  const repo = 'images2';
  const path = `${folder}/${filename}`.replace(/(^\/)|(\/$)/g, ''); // 移除路径开头和结尾的斜杠
  const token = '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';
  console.log(contentBase64.length);
  const url = `https://api.github.com/repos/${owner}/${repo}/contents/${path}`;

  // 首先检查文件是否已存在
  let response = await fetch(url, {
    method: 'GET',
    headers: {
      'Authorization': `token ${token}`,
      'User-Agent': 'cloudflare-worker-github'
    }
  });

  if (response.ok) {
    // 文件已存在，直接返回文件的链接
    const json = await response.json();
    return new Response(json.download_url, {
      headers: { 'Content-Type': 'text/plain' },
      status: 200
    });
  } else if (response.status === 404) {
    // 文件不存在，上传文件
    const body = JSON.stringify({
      message: `Upload ${filename}`,
      content: contentBase64
    });

    response = await fetch(url, {
      method: 'PUT',
      headers: {
        'Authorization': `token ${token}`,
        'Content-Type': 'application/json',
        'User-Agent': 'cloudflare-worker-github'
      },
      body: body
    });

    const json = await response.json();
    console.log(JSON.stringify(json));
    if (response.ok) {
      return new Response(json.content.download_url, {
        headers: { 'Content-Type': 'text/plain' },
        status: 200
      });
    } else {
      return new Response(JSON.stringify(json), {
        headers: { 'Content-Type': 'application/json' },
        status: response.status
      });
    }
  } else {
    // 其他错误
    return new Response(JSON.stringify(), { status: response.status })
  }
}
