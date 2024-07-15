# gh-compr

A simple script I made to help me review cherry-picked pull requests where diffs are expected to be similar.
It fetches the PRs' diffs using the GitHub API so it works on deleted branches too.
It outputs a (cleaned up) diff of the PRs' diffs.

## Installation

```bash
gh extension install https://github.com/samugi/gh-compr
```

## Usage

```bash
gh compr <PR 1 URL> <PR 2 URL>
```
