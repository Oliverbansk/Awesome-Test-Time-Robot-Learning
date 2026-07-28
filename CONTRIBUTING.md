# Contributing

Thank you for helping maintain Awesome Test-Time Robot Learning.

## What Belongs in the List

A submission should:

1. study a learned robot policy;
2. improve that policy using context, computation, data, or interaction available at deployment;
3. report enough methodological or empirical detail to identify the deployment-time update mechanism;
4. provide a stable paper URL, preferably an arXiv abstract page, proceedings page, or publisher page.

The list is mechanism-first. Choose the line that captures the paper's primary deployment-time intervention:

- `rl-post-training-and-adaptation`
- `test-time-policy-steering`
- `test-time-training`
- `in-context-learning-and-prompting`
- `scaling-verification`

Use tags to record important secondary mechanisms rather than duplicating a paper across lines.

## Adding a Paper

1. Add one object to the appropriate `papers` array in `data/papers.json`.
2. Use the first public release date in `YYYY-MM-DD` format.
3. Keep papers sorted from oldest to newest within each line.
4. Use the accepted venue when known; otherwise use `arXiv`.
5. Add project and code URLs only when they are official.
6. Run:

```bash
python3 scripts/validate_data.py
python3 scripts/build_readme.py
python3 scripts/build_readme.py --check
```

Commit both `data/papers.json` and the regenerated `README.md`.

## Data Format

Required paper fields:

```json
{
  "date": "2026-01-01",
  "title": "Paper title",
  "venue": "Conference 2026",
  "paper": "https://arxiv.org/abs/0000.00000",
  "tags": ["Test-Time Learning", "Robot Manipulation"]
}
```

Optional fields are `project` and `code`.

## Quality Bar

- Prefer exact paper titles and official links.
- Do not use the latest revision date when an earlier public release exists.
- Keep tags concise and mechanism-oriented.
- Avoid promotional claims in titles, tags, or line descriptions.
- Explain ambiguous classification in the pull request.
