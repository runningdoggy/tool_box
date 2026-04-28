# Tool Box

个人常用小工具集合。每个工具都放在独立目录里，目录内包含自己的 `README.md`、运行脚本和依赖说明。

## 工具列表

| 工具 | 用途 | 入口 |
| --- | --- | --- |
| `video_script_transcriber/` | 批量从视频 URL 流式提取音频并转写脚本，支持 Excel/TXT/CSV 汇总输出和中文二次校准。 | [`video_script_transcriber/README.md`](video_script_transcriber/README.md) |
| `youdao_link_reader/` | 解析有道云笔记公开分享链接，导出标题和正文纯文本，方便继续摘要或结构化整理。 | [`youdao_link_reader/README.md`](youdao_link_reader/README.md) |

## 快速使用

### 视频脚本转写

```bash
cd video_script_transcriber
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python auto_export_pipeline.py --input urls.txt --output-dir output_auto --model tiny --language zh
```

### 有道分享链接阅读

```bash
cd youdao_link_reader
python3 youdao_link_reader.py 'https://share.note.youdao.com/s/XXXX'
```

## 新增工具规范

- 每个工具放在独立目录，目录名使用英文小写和下划线。
- 每个工具目录都保留独立 `README.md`，说明用途、安装、运行方式和限制。
- 不提交本地数据、账号 token、`.env`、输出文件、虚拟环境和缓存。
