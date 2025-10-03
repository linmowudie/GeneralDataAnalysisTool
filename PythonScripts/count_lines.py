"""
统计 Python 项目代码行数（Windows 兼容版）

功能：
- 遍历指定目录下的所有 .py 文件
- 统计：代码行、注释行、空行
- 自动排除常见不需要的目录（如 venv, __pycache__, .git, .vscode 等）
- 支持通过命令行传入路径和自定义排除目录
- 兼容 Windows 路径（如 C:\ 与反斜杠）

使用方式：
    python count_lines.py [路径] [--exclude dir1 dir2 ...]

示例：
    python count_lines.py C:\\myproject
    python count_lines.py . --exclude venv __pycache__ .git tests
"""

import os
import sys
import argparse
from pathlib import Path


def is_excluded(path: Path, exclude_dirs: set) -> bool:
    """判断路径是否包含被排除的目录（不区分大小写，Windows 友好）"""
    return any(part.lower() in exclude_dirs for part in path.parts) or \
           path.name.lower() in exclude_dirs


def count_lines_in_file(file_path: Path) -> tuple[int, int, int]:
    """
    统计单个 Python 文件的代码行数
    返回: (代码行, 注释行, 空行)
    """
    code_lines = 0
    comment_lines = 0
    blank_lines = 0
    in_multiline_string = False
    quote_char = ""

    try:
        # Windows 常见编码兼容：utf-8、gbk（防止中文路径或文件报错）
        encoding = 'utf-8'
        with open(file_path, 'r', encoding=encoding) as f:
            lines = f.readlines()
    except UnicodeDecodeError:
        try:
            encoding = 'gbk'
            with open(file_path, 'r', encoding=encoding) as f:
                lines = f.readlines()
        except Exception:
            print(f"  跳过文件（编码错误）: {file_path}")
            return 0, 0, 0
    except (PermissionError, OSError) as e:
        print(f"  跳过文件（权限错误）: {file_path} - {e}")
        return 0, 0, 0

    for line in lines:
        line = line.strip()

        # 空行
        if not line:
            blank_lines += 1
            continue

        # 多行字符串处理（''' 或 """）
        if not in_multiline_string:
            if line.startswith("'''") or line.startswith('"""'):
                in_multiline_string = True
                quote_char = line[:3]
                comment_lines += 1
            elif line.startswith('#'):
                comment_lines += 1
            else:
                code_lines += 1
        else:
            comment_lines += 1
            if line.endswith(quote_char):
                in_multiline_string = False

    return code_lines, comment_lines, blank_lines


def main():
    parser = argparse.ArgumentParser(description="统计 Python 项目代码行数")
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="项目根目录路径（默认当前目录）"
    )
    parser.add_argument(
        "--exclude",
        nargs="*",
        default=[
            "venv", ".venv", "__pycache__", ".git", ".hg", ".svn",
            ".idea", ".vscode", "node_modules", "dist", "build", "pycache"
        ],
        help="要排除的目录名（默认已包含常见目录）"
    )

    args = parser.parse_args()

    root = Path(args.path).resolve()

    if not root.exists():
        print(f"错误：路径不存在 -> {root}")
        sys.exit(1)

    if not root.is_dir():
        print(f"错误：路径不是目录 -> {root}")
        sys.exit(1)

    # 转为小写集合，提高匹配兼容性（Windows 不区分大小写）
    exclude_dirs = {d.lower() for d in args.exclude}

    total_code = 0
    total_comment = 0
    total_blank = 0
    file_count = 0

    print(f"开始扫描目录: {root}")
    print(f"排除目录: {', '.join(args.exclude)}\n")

    # 使用 rglob 安全遍历所有 .py 文件
    for py_file in root.rglob("*.py"):
        if is_excluded(py_file.relative_to(root), exclude_dirs):
            continue

        code, comment, blank = count_lines_in_file(py_file)
        total_code += code
        total_comment += comment
        total_blank += blank
        file_count += 1

        # 可选：打印每个文件的统计（取消注释即可）
        # print(f"{py_file.relative_to(root)} -> 代码:{code} 注释:{comment} 空行:{blank}")

    # 输出汇总
    print("=" * 60)
    print("Python 项目代码统计结果")
    print("=" * 60)
    print(f"扫描文件数量: {file_count}")
    print(f"总代码行数:   {total_code}")
    print(f"总注释行数:   {total_comment}")
    print(f"总空行数:     {total_blank}")
    print(f"总计行数:     {total_code + total_comment + total_blank}")
    print("=" * 60)


if __name__ == "__main__":
    main()