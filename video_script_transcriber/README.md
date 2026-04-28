# 批量视频脚本提取

这个工具会读取链接列表，直接从 URL 流式提取音频（不落地保存视频文件），并用 Whisper 自动转写成文本，最终汇总成单个 Excel/TXT 文件。

## 1) 安装依赖

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

默认会优先使用系统 `ffmpeg`，若没有，会自动尝试使用 `imageio-ffmpeg` 提供的二进制。

## 2) 准备链接文件

支持两种格式：

- `txt`：每行一个链接（也允许每行包含其他文字，程序会自动提取 URL）
- `csv/tsv`：优先读取 `url` / `video_url` / `link` / `mp4_url` 列
- `xlsx`：自动扫描工作簿中的文本和超链接单元格并提取 URL

示例 `urls.txt`：

```txt
https://tos.mobgi.com/tos_beijing/material_4/20260414/12400079443/12400079443/4cf2c6369bbcb49cb982eddcbbccfa4f.mp4
```

## 3) 运行

```bash
python3 extract_video_scripts.py --input urls.txt --output-dir output --model small --language zh
```

常用参数：

- `--language auto`：自动识别语言（默认）
- `--keep-audio`：保留中间音频
- `--ffmpeg-bin /path/to/ffmpeg`：指定 ffmpeg 路径

## 4) 输出结果

- `output/scripts.xlsx`：汇总表（第一列链接，第二列脚本）
- `output/scripts.txt`：汇总文本（每行：链接 + `\t` + 脚本）
- `output/results.csv`：任务状态明细（成功/失败 + 错误信息）

## 5) 一键自动导出（不需要手动逐步执行）

### 命令行一键跑

```bash
source .venv/bin/activate
python auto_export_pipeline.py \
  --input urls.txt \
  --output-dir output_auto \
  --model tiny \
  --language zh
```

默认会自动执行：

1. 批量转写（`extract_video_scripts.py`）
2. 二次校准（`review_and_fix_scripts.py`）
3. 输出最终文件：
   - `output_auto/scripts_final.xlsx`
   - `output_auto/scripts_final.txt`
   - `output_auto/scripts_final_review.csv`

### 双击一键启动（macOS）

你可以直接双击：

- `一键导出脚本.command`

也支持命令行传参：

```bash
./一键导出脚本.command /路径/你的链接.csv /路径/输出目录
```

## 6) 中文脚本二次修正（可选）

如果你觉得部分中文识别不够准确，可以对 `scripts.xlsx` 做一轮“逻辑修正 + 质检打标”：

```bash
python3 review_and_fix_scripts.py \
  --input output/scripts.xlsx \
  --output-dir output \
  --output-prefix scripts_corrected
```

会生成：

- `output/scripts_corrected.xlsx`：含原脚本、修正脚本、质量评分/等级
- `output/scripts_corrected.txt`：每行链接 + 修正脚本
- `output/scripts_corrected_review.csv`：质检标签明细

### 接入开源大模型校准（HF Inference）

如果你有 `HF_TOKEN`，可以让开源模型做二次语义校准（比如 `1TF -> ETF`、同音错词修正）：

```bash
export HF_TOKEN=你的token
python3 review_and_fix_scripts.py \
  --input output/scripts.xlsx \
  --output-dir output \
  --output-prefix scripts_corrected_llm \
  --llm-backend hf \
  --llm-model Qwen/Qwen2.5-7B-Instruct \
  --llm-scope low \
  --llm-max-rows 80
```

说明：

- `--llm-scope low`：只处理低质量行（推荐）
- `--llm-scope suspicious`：处理可疑行（如含 `1TF/ITF`）
- `--llm-scope all`：处理全部行（最慢）

## 7) 已有关联表二次校准（可选）

如果你已经把脚本合并回原始素材表，并且表里有 `脚本信息` 列，可以直接生成校准版：

```bash
python3 calibrate_etf_workbook.py \
  --input your_material_report.xlsx \
  --output your_material_report_calibrated.xlsx
```

默认会新增：

- `脚本信息_校准`
- `脚本质量评分`
- `脚本质量等级`
- `校准说明`
