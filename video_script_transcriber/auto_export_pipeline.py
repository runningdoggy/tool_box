#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="一键批量转写并导出最终汇总文件。")
    parser.add_argument("--input", required=True, help="输入链接文件（txt/csv/tsv）")
    parser.add_argument("--output-dir", required=True, help="输出目录")
    parser.add_argument("--model", default="tiny", help="Whisper 模型（默认 tiny）")
    parser.add_argument("--language", default="zh", help="语言（默认 zh）")
    parser.add_argument("--timeout", type=int, default=90, help="读取超时秒数")
    parser.add_argument(
        "--skip-review",
        action="store_true",
        help="只做转写，不做二次校准",
    )
    return parser.parse_args()


def run_command(command: list[str], cwd: Path) -> None:
    process = subprocess.run(command, cwd=str(cwd))
    if process.returncode != 0:
        raise RuntimeError(f"命令执行失败：{' '.join(command)}")


def copy_final_files(output_dir: Path, prefix: str) -> None:
    mapping = {
        output_dir / f"{prefix}.xlsx": output_dir / "scripts_final.xlsx",
        output_dir / f"{prefix}.txt": output_dir / "scripts_final.txt",
        output_dir / f"{prefix}_review.csv": output_dir / "scripts_final_review.csv",
    }
    for source, target in mapping.items():
        if source.exists():
            shutil.copy2(source, target)


def main() -> int:
    args = parse_args()
    root = Path(__file__).resolve().parent
    input_path = Path(args.input).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    if not input_path.exists():
        print(f"输入文件不存在：{input_path}")
        return 1

    try:
        print("步骤 1/2：开始转写...")
        run_command(
            [
                sys.executable,
                str(root / "extract_video_scripts.py"),
                "--input",
                str(input_path),
                "--output-dir",
                str(output_dir),
                "--model",
                args.model,
                "--language",
                args.language,
                "--timeout",
                str(args.timeout),
            ],
            cwd=root,
        )

        if args.skip_review:
            print("已跳过二次校准。")
            print(f"输出：{output_dir / 'scripts.xlsx'}")
            print(f"输出：{output_dir / 'scripts.txt'}")
            print(f"输出：{output_dir / 'results.csv'}")
            return 0

        print("步骤 2/2：开始校准...")
        review_prefix = "scripts_corrected_auto"
        run_command(
            [
                sys.executable,
                str(root / "review_and_fix_scripts.py"),
                "--input",
                str(output_dir / "scripts.xlsx"),
                "--output-dir",
                str(output_dir),
                "--output-prefix",
                review_prefix,
            ],
            cwd=root,
        )
        copy_final_files(output_dir, review_prefix)
        print(f"输出：{output_dir / 'scripts_final.xlsx'}")
        print(f"输出：{output_dir / 'scripts_final.txt'}")
        print(f"输出：{output_dir / 'scripts_final_review.csv'}")
        print("完成。")
        return 0
    except Exception as error:
        print(f"运行失败：{error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
