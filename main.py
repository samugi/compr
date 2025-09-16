from typing import List
import re
import subprocess
import sys
from pr_diff import Pr, PrDiff, FileDiff, Hunk
from diff_report import DiffReport
from report_formatter import format_pr_diff_report_markdown


def process_input():
    url1 = sys.argv[1]
    url2 = sys.argv[2]
    return url1, url2


def main():
    url1, url2 = process_input()
    pr1 = Pr(url1)
    pr2 = Pr(url2)
    diff_report = DiffReport(pr1, pr2)

    output = format_pr_diff_report_markdown(diff_report.to_dict())
    print(output)


if __name__ == "__main__":
  main()
