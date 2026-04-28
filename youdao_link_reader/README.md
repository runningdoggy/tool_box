# Youdao Link Reader（有道分享链接阅读器）

把有道云笔记公开分享链接（`share.note.youdao.com`）解析成纯文本，方便继续做摘要/结构化整理。

## 使用

```bash
python3 youdao_link_reader.py 'https://share.note.youdao.com/s/XXXX'
```

## 支持的链接形式

- `https://share.note.youdao.com/s/<短码>`
- `https://share.note.youdao.com/noteshare?id=<shareKey>`

## 限制

- 仅支持“公开分享、无密码、无需登录可访问”的链接
- 若运行环境限制外网访问（例如某些沙盒环境），需要放开网络权限才能抓取正文

## 输出

- 标题（`# ...`）
- 正文纯文本（按段落/行输出）
