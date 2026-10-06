"""GUIDE Phần 3 - Người tuyển chọn skill (skill curator): tự viết skill từ các lần chạy thất bại.   >>> SINH VIÊN CÀI ĐẶT curate_skills <<<

Pseudo-code: guides/pseudocode/04_curator.md
Kiểm tra:    pytest tests/test_04_curator.py
Chạy thật:   python -m lab.curator
"""
import re
from pathlib import Path

from .tasks import eval_markers   # có sẵn: định danh của tác vụ đánh giá, tính lúc chạy

# ---- CÓ SẴN, KHÔNG SỬA: kiểm tra và tách khối skill (phần dễ sai và liên quan bảo mật) ----------------
SAFE_NAME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def validate_skill(text: str, expected_name: str | None = None) -> list[str]:
    """Kiểm tra nội dung một SKILL.md. Trả về danh sách vấn đề (rỗng = hợp lệ).

    Quy tắc: có khối YAML frontmatter; `name` chữ thường/số/gạch ngang (tối đa 64 ký tự) và bằng `expected_name`
    nếu được truyền; có `description` (tối đa 1024 ký tự); phần thân tối đa 80 dòng; không chứa chuỗi nào của
    `eval_markers()`. Quy tắc về `name` cũng là biện pháp bảo mật: tên khối do LLM sinh ra được dùng để tạo
    đường dẫn, nên `../evil` không được lọt qua.
    """
    problems = []
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text.strip() + "\n", re.S)
    if not m:
        return ["missing YAML frontmatter"]
    front, body = m.groups()
    name = re.search(r"^name:\s*(.+)$", front, re.M)
    desc = re.search(r"^description:\s*(.+)$", front, re.M)
    n = name.group(1).strip() if name else ""
    if not SAFE_NAME.fullmatch(n) or len(n) > 64:
        problems.append("invalid name")
    elif expected_name is not None and n != expected_name:
        problems.append("name differs from the block name")
    if not desc or len(desc.group(1).strip()) > 1024:
        problems.append("missing or too long description")
    if len(body.strip().splitlines()) > 80:
        problems.append("body longer than 80 lines")
    low = text.lower()
    for marker in eval_markers():
        if marker in low:
            problems.append(f"mentions evaluation material: {marker}")
    return problems


def parse_skill_blocks(reply: str) -> list[tuple[str, str]]:
    """Tách câu trả lời của LLM thành danh sách (name, nội dung SKILL.md).

    Khuôn dạng: `=== SKILL: <name> ===` ... `=== END ===`. Một khối kết thúc ở điểm nào đến trước trong ba điểm:
    `=== END ===`, tiêu đề `=== SKILL:` kế tiếp, hoặc cuối văn bản (LLM đôi khi quên dòng END).
    """
    pattern = re.compile(r"^=== SKILL: (\S+) ===[ \t]*\n(.*?)(?=^=== END ===|^=== SKILL: |\Z)", re.S | re.M)
    return [(name, text.strip()) for name, text in pattern.findall(str(reply))]
# --------------------------------------------------------------------------------------------------


import json

from .model import make_model
from .tasks import ROOT, eval_markers   # có sẵn: định danh của tác vụ đánh giá, tính lúc chạy


def curate_skills(results_dir="results", source_condition="baseline", out_dir=None, model=None, max_skills: int = 3) -> list[Path]:
    """Đọc các lần chạy của TÁC VỤ HỌC (role == "learn") trong `source_condition`, nhờ LLM viết skill, ghi file.

    Các bước: nạp run.json + trace.md -> (nếu không có check nào thất bại: in cảnh báo và trả về [] mà KHÔNG gọi LLM)
    -> dựng prompt -> model.invoke(prompt) -> parse_skill_blocks -> validate_skill(text, expected_name=name)
    -> ghi `<out_dir>/<name>/SKILL.md`. Mặc định `out_dir` = <gốc lab>/skills/auto (dùng `ROOT` từ lab.tasks).
    Giữ tối đa `max_skills` skill hợp lệ; skill không hợp lệ bị bỏ qua.
    Prompt chứa, với mỗi check thất bại, TÊN và trường `detail` (lời nhận xét của bot đánh giá: phát biểu quy tắc bị vi phạm)
    cùng phần cuối của vết (trace). Với tác vụ học, `detail` chỉ phát biểu quy tắc, không chứa đáp án.
    Tuyệt đối KHÔNG đưa dữ liệu của tác vụ đánh giá (role == "eval") vào prompt.
    model mặc định: make_model() (lab.model).
    Trả về: danh sách đường dẫn SKILL.md đã ghi.
    """
    if out_dir is None:
        out_dir = ROOT / "skills" / "auto"
    else:
        out_dir = Path(out_dir)

    results_path = Path(results_dir) / source_condition
    runs = []
    if results_path.exists():
        for run_file in sorted(results_path.glob("*/run.json")):
            try:
                r = json.loads(run_file.read_text(encoding="utf-8"))
            except Exception:
                continue
            if r.get("role") != "learn":
                continue
            trace_file = run_file.parent / "trace.md"
            trace_content = trace_file.read_text(encoding="utf-8") if trace_file.exists() else ""
            trace_tail = trace_content[-6000:] if len(trace_content) > 6000 else trace_content
            failed = []
            for c in r.get("checks", []):
                if not c.get("passed"):
                    failed.append((c.get("name", ""), c.get("detail", "")))
            if failed:
                runs.append({
                    "task": r.get("task", run_file.parent.name),
                    "failed": failed,
                    "trace": trace_tail,
                })

    if not runs:
        print("Warning: không có check thất bại ở tác vụ học.")
        return []

    prompt_lines = [
        "You are writing reusable SKILL files for an autonomous software engineering and data analysis agent.",
        "Below are the failed checks (check name and evaluation bot feedback) and execution traces from recent runs.",
        f"Identify common procedural mistakes and write at most {max_skills} concise skills that help avoid these mistakes on new tasks.",
        "",
        "Rules:",
        "- Skills must be general: do not mention specific task IDs, exact task workspace files, specific numbers, or specific test solutions.",
        "- Each skill must have YAML frontmatter with 'name' (lowercase, numbers, and hyphens) and 'description' (one sentence: WHEN to use this skill).",
        "- The body should be an imperative checklist or procedure of at most 40 lines.",
        "- Output format exactly:",
        "=== SKILL: <name> ===",
        "---",
        "name: <name>",
        "description: <when to use>",
        "---",
        "<body content>",
        "=== END ===",
        "",
        "Failed runs:",
    ]
    for run in runs:
        prompt_lines.append(f"Task: {run['task']}")
        prompt_lines.append("Failed checks:")
        for name, detail in run["failed"]:
            prompt_lines.append(f"  - {name}: {detail}")
        prompt_lines.append(f"Trace snippet:\n{run['trace']}\n")

    prompt = "\n".join(prompt_lines)

    if model is None:
        model = make_model()

    response = model.invoke(prompt)
    reply_content = response.content if hasattr(response, "content") else str(response)

    written = []
    for name, text in parse_skill_blocks(reply_content):
        if len(written) >= max_skills:
            break
        problems = validate_skill(text, expected_name=name)
        if problems:
            continue
        skill_file = out_dir / name / "SKILL.md"
        skill_file.parent.mkdir(parents=True, exist_ok=True)
        skill_file.write_text(text, encoding="utf-8")
        written.append(skill_file)

    return written


if __name__ == "__main__":
    for p in curate_skills():
        print("wrote", p)
