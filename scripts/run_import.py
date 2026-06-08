"""一键执行：生成 Word → 导入 CSV → 补充 Word 关系数据。"""
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent


def run(script: str):
    print(f"\n>>> 运行 {script}")
    subprocess.run([sys.executable, str(SCRIPTS / script)], check=True)


def main():
    run("generate_docx.py")
    run("import_csv.py")
    run("extract_docx.py")
    print("\n全部导入完成。")


if __name__ == "__main__":
    main()
