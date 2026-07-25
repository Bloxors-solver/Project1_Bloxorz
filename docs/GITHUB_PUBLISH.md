# Publish the complete project history to GitHub

Target repository:

```text
https://github.com/tuhuynhhhh/Project1_Bloxorz
```

These steps assume the GitHub repository is empty.

## 1. Final checks

```bat
cd /d D:\AI_Project\source\Bloxorz_AI_Phase1
git status
python -m unittest discover -s tests -p "test_*.py" -v
```

Commit all final documentation and source changes before publishing.

## 2. Merge the final feature branch

Check branches:

```bat
git branch
```

A safe approach is to create `main` from the final compliance branch:

```bat
git switch feature/requirements-compliance
git switch -c main
```

If `main` already exists:

```bat
git switch main
git merge --no-ff feature/requirements-compliance
```

## 3. Configure the remote

```bat
git remote -v
```

No `origin` yet:

```bat
git remote add origin https://github.com/tuhuynhhhh/Project1_Bloxorz.git
```

Wrong `origin`:

```bat
git remote set-url origin https://github.com/tuhuynhhhh/Project1_Bloxorz.git
```

## 4. Push main, all feature branches, and tags

```bat
git push -u origin main
git push origin --all
git push origin --tags
```

This preserves the complete phase history rather than publishing only the final files.

## 5. Verify GitHub

Confirm the repository contains:

- `main.py`
- `game/`
- `search_algorithms/`
- `tests/`
- `levels/`
- final README and sources
- benchmark scripts and selected final results
- docs and report
- tags such as `phase6b-stable` and `phase7-ui-stable`
- feature branches

## 6. Do not upload

These should be absent due to `.gitignore`:

- `.venv/`
- `__pycache__/`
- `*.pyc`
- `backup/`
- `reference/`
- temporary logs
- `dist/`

If one was tracked previously, remove it from Git without deleting the local copy:

```bat
git rm -r --cached .venv __pycache__ backup reference
git commit -m "chore: remove generated and reference files from repository"
```
