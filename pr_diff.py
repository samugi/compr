import subprocess
import re
import hashlib
from typing import List

def compute_md5(data: str) -> str:
    return hashlib.md5(data.encode('utf-8')).hexdigest()

class Hunk:
    def __init__(self, text: str):
        self.text = text.strip()
        self.md5 = self._compute_md5(self.text)

    @staticmethod
    def _compute_md5(data: str) -> str:
        return hashlib.md5(data.encode('utf-8')).hexdigest()

    def __repr__(self):
        return f"<Hunk md5={self.md5} length={len(self.text)}>"

    def pretty_print(self):
        print("\t\t", self)


class FileDiff:
    """Represents the diff for a single file, containing multiple hunks."""

    def __init__(self, file_path: str, diff_text: str):
        self.file_path = file_path
        self.diff_text = diff_text.strip()
        self.md5 = compute_md5(self.diff_text)
        self.hunks = self._parse_hunks(self.diff_text)

    def _parse_hunks(self, text: str) -> List[Hunk]:
        """Extract all hunks from the file diff."""
        parts = re.split(r'(?=^@@ )', text, flags=re.MULTILINE)
        return [Hunk(part) for part in parts if part.strip().startswith('@@')]

    def __repr__(self):
        return f"<FileDiff path=['{self.file_path}'] md5=[{self.md5}] hunks=[{len(self.hunks)}]>"

    def pretty_print(self):
        print("\t", self)
        for hunk in self.hunks:
            hunk.pretty_print()


class PrDiff:
    """Represents the entire PR diff, containing multiple file diffs."""

    def __init__(self, diff_text: str):
        self.diff_text = diff_text.strip()
        self.md5 = compute_md5(self.diff_text)
        self.file_diffs = self._parse_chunks(self.diff_text)


    def _parse_chunks(self, diff_text: str) -> List[FileDiff]:
        """Split the PR diff into individual file diffs."""
        # Split on "diff --git" lines
        raw_chunks = re.split(r'(?=^diff --git)', diff_text, flags=re.MULTILINE)
        raw_chunks = [chunk.strip() for chunk in raw_chunks if chunk.strip()]

        file_diffs = []
        for chunk in raw_chunks:
            lines = chunk.splitlines()

            # Extract file path from the first line
            # Format: diff --git a/path/to/file b/path/to/file
            match = re.match(r'^diff --git a/(.+?) b/\1$', lines[0])
            if match:
                file_path = match.group(1)
            else:
                # Fallback if exact match fails
                file_path = lines[0].split()[2][2:]

            file_diffs.append(FileDiff(file_path, chunk))

        return file_diffs

    def __repr__(self):
        return f"<PrDiff md5=[{self.md5}] files=[{len(self.chunks)}]>"

    def pretty_print(self):
        print(self)
        for chunk in self.chunks:
            chunk.pretty_print()

class Pr:
    def __init__(self, url: str):
        owner, repo, pull_number = self._validate_url_extract_info(url)
        self.url = url
        self.repo = repo
        self.number = pull_number

        raw_pr_diff = self._download_pr_diff(url)
        self.pr_diff = PrDiff(raw_pr_diff)

    def __repr__(self):
        return f"<Pr number=[{self.number}] diff_md5=[{self.pr_diff.md5}] files=[{len(self.pr_diff.chunks)}]>"

    def to_markdown(self):
        return f"PR *#{self.number}*, diff md5: *{self.pr_diff.md5}*, files: *{len(self.pr_diff.chunks)}*"


    @staticmethod
    def _download_pr_diff(pr_url: str):
        completed_process = subprocess.run(["gh", "pr", "diff", pr_url], capture_output=True, text=True)
        if completed_process.returncode != 0:
            print(completed_process.stderr, file=sys.stderr)
            raise RuntimeError(f"Could not download pr diff from: {pr_url}")
        return completed_process.stdout

    @staticmethod
    def _validate_url_extract_info(url: str) -> (str, str, str):
        """
        Validate a GitHub pull request URL.

        :param url: The GitHub PR URL to validate.
        :return: True if successful.
        :raises ValueError: If the URL does not match the expected format.
        """
        regex = r"^https://github\.com/([a-zA-Z0-9-]+)/([a-zA-Z0-9-]+)/pull/([0-9]+)$"
        match = re.match(regex, url)

        if not match:
            raise ValueError(
                f"PR URL '{url}' does not match the expected format: "
                "'https://github.com/<owner>/<repo>/pull/<number>'"
            )

        owner, repo, pull_number = match.groups()
        return owner, repo, int(pull_number)

