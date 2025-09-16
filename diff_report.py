from typing import List, Optional, Dict, Any
from pr_diff import Pr

class DiffReport:
    """
    Compares two PrDiff objects and produces a structured report of differences.
    """

    def __init__(self, pr1: Pr, pr2: Pr):
        self.pr1 = pr1
        self.pr2 = pr2

        # Final structured output
        self.identical_files: List[str] = []
        self.different_files: Dict[str, List[Any]] = {}
        self.generate()

    def generate(self):
        """Generate the report data structure by comparing two PR diffs."""
        pr1_files = {f.file_path: f for f in self.pr1.pr_diff.file_diffs}
        pr2_files = {f.file_path: f for f in self.pr2.pr_diff.file_diffs}

        all_files = sorted(set(pr1_files.keys()) | set(pr2_files.keys()))

        for file_path in all_files:
            file1 = pr1_files.get(file_path)
            file2 = pr2_files.get(file_path)

            if file1 and file2:
                if file1.md5 == file2.md5:
                    self.identical_files.append(file_path)
                else:
                    aligned = self._align_hunks(file1.hunks, file2.hunks)
                    self.different_files[file_path] = aligned
            else:
                aligned = []
                if file1 and not file2:
                    aligned = self._align_hunks(file1.hunks, [])
                elif file2 and not file1:
                    aligned = self._align_hunks([], file2.hunks)

                self.different_files[file_path] = aligned

    def _align_hunks(self, hunks1: List, hunks2: List) -> List[Dict[str, Optional[str]]]:
        """
        Align two lists of hunks based on md5 matching.
        Returns a list of dicts with left/right hunks aligned.
        """
        aligned = []
        h1_index, h2_index = 0, 0
        total_h1, total_h2 = len(hunks1), len(hunks2)

        while h1_index < total_h1 or h2_index < total_h2:
            current_h1 = hunks1[h1_index] if h1_index < total_h1 else None
            current_h2 = hunks2[h2_index] if h2_index < total_h2 else None

            # CASE 1: One list is exhausted → treat remaining as extras
            if current_h1 is not None and current_h2 is None:
                aligned.append({"left": current_h1, "right": None})
                h1_index += 1

            elif current_h1 is None and current_h2 is not None:
                aligned.append({"left": None, "right": current_h2})
                h2_index += 1

            # CASE 2: Both lists have hunks
            else:
                # CASE 2A: Direct match
                if current_h1.md5 == current_h2.md5:
                    aligned.append({"left": current_h1, "right": current_h2})
                    h1_index += 1
                    h2_index += 1

                # CASE 2B: Look ahead in the right side to find match for current_h1
                else:
                    found_h2_match_index = None
                    lookahead_index = h2_index + 1

                    # Scan the rest of the hunks2 list
                    while found_h2_match_index is None and lookahead_index < total_h2:
                        if hunks2[lookahead_index].md5 == current_h1.md5:
                            found_h2_match_index = lookahead_index
                        else:
                            lookahead_index += 1

                    if found_h2_match_index is not None:
                        # Extra right hunks before the match
                        for extra_h2 in hunks2[h2_index:found_h2_match_index]:
                            aligned.append({"left": None, "right": extra_h2})

                        # Match found
                        aligned.append({
                            "left": current_h1,
                            "right": hunks2[found_h2_match_index]
                        })

                        # Update both indexes
                        h1_index += 1
                        h2_index = found_h2_match_index + 1

                    # CASE 2C: No match found at all → extra left hunk
                    else:
                        aligned.append({"left": current_h1, "right": None})
                        h1_index += 1

        return aligned


    def to_dict(self) -> Dict[str, Any]:
        """Return the final structured report as a dictionary."""
        return {
            "left_pr": self.pr1,
            "right_pr": self.pr2,
            "identical_files": self.identical_files,
            "different_files": self.different_files,
        }
