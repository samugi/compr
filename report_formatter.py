from typing import List, Dict, Optional


def format_pr_diff_report_markdown(report_data: Dict) -> str:
    """
    Format a PR diff report into Markdown + HTML with:
    - File-level summary at the top
    - Collapsible sections for each file that differs
    - A list of identical files
    """
    lines = []

    _add_header_section(lines, report_data)

    if report_data["different_files"].items():
        _add_pr_diff_summary_section(lines, report_data)

    if report_data["identical_files"]:
        _add_identical_fiels_section(lines, report_data)

    return "\n".join(lines)


def _add_header_section(lines: List[str], report_data: Dict):
    # --- File-level summary ---
    total_files = len(report_data["identical_files"]) + len(report_data["different_files"])
    total_identical = len(report_data["identical_files"])
    total_different = len(report_data["different_files"].keys())

    similarity_ratio = total_identical / total_files if total_files else 1.0

    lines.append(f"# Similarity: {similarity_ratio * 100:.1f}%\n")
    lines.append("Compared: ")
    lines.append("- left: " + report_data["left_pr"].url)
    lines.append("- right: " + report_data["right_pr"].url)
    lines.append("")
    lines.append(f"{_generate_emoji_chart(total_identical, total_different)}\n")

    lines.append("<hr/>") # separate sections


def _add_pr_diff_summary_section(lines: List[str], report_data: Dict):
    total_files = len(report_data["identical_files"]) + len(report_data["different_files"])
    total_identical = len(report_data["identical_files"])
    total_different = len(report_data["different_files"].keys())

    lines.append("<details>")
    lines.append("<summary><h3>PR Diff Summary</h3></summary>\n")
    lines.append("<ul>")
    lines.append(f"<li>Total files compared: {total_files}</li>")
    lines.append(f"<li>Files identical: {total_identical}</li>")
    lines.append(f"<li>Files with differences: {total_different}\n</li>")
    lines.append("</ul>\n")

    left_pr = report_data["left_pr"]
    right_pr = report_data["right_pr"]

    # --- Different files ---
    for filename, aligned_hunks in report_data["different_files"].items():
        lines.append(f"<details>")
        lines.append(f"<summary>📄 {filename}</summary>\n")
        lines.append("<table style='table-layout: fixed; width: 100%;'>")
        lines.append("<tr>")
        lines.append("<th style='width: 5%'>#</th>")
        lines.append(f"<th style='width: 47.5%'>\n\n[PR #{left_pr.number}]({left_pr.url})\n\n</th>")
        lines.append(f"<th style='width: 47.5%'>\n\n[PR #{right_pr.number}]({right_pr.url})\n\n</th>")
        lines.append("</tr>")

        for idx, pair in enumerate(aligned_hunks, start=1):
            left_hunk = pair["left"]
            right_hunk = pair["right"]

            if left_hunk and right_hunk and left_hunk.md5 == right_hunk.md5:
                lines.append("<tr>")
                lines.append(f"<td>{idx}</td>")
                lines.append(f"<td colspan='2'>Hunk is identical (md5: <code>{left_hunk.md5}</code>)</td>")
                lines.append("</tr>")
            else:
                left_text = _render_hunk(left_hunk)
                right_text = _render_hunk(right_hunk)
                lines.append("<tr>")
                lines.append(f"<td>{idx}</td>")
                lines.append(f"<td>\n{left_text}\n</td>")
                lines.append(f"<td>\n{right_text}\n</td>")
                lines.append("</tr>")

        lines.append("</table>\n")
        lines.append("</details>\n")  # end collapsible section

    lines.append("</details>") # end Pr Diff summary


def _add_identical_fiels_section(lines: List[str], report_data: Dict):
    lines.append("<details>")
    lines.append("<summary><h3>Identical files</h3></summary>\n")
    for file_path in report_data["identical_files"]:
        lines.append(f"- `{file_path}`")
    lines.append("</details>\n")


def _generate_emoji_chart(identical: int, different: int, total_segments: int = 10) -> str:
    """Generate a simple emoji chart for similarity."""
    total_files = identical + different
    filled = int(total_segments * identical / total_files) if total_files else total_segments
    empty = total_segments - filled
    return f"Similarity: {'🟩' * filled}{'🟥' * empty} ({identical}/{total_files} identical)"


def _render_hunk(hunk: Optional[object]) -> str:
    """
    Render a single hunk into HTML-safe diff block.
    """
    if hunk is None:
        return "(no changes)"

    return f"\n```diff\n{hunk.text}\n```\n"
