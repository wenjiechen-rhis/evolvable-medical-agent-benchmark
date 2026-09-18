# Release 0.1.0

Recommended repository name: `evolvable-medical-agent-benchmark`

Recommended description: `Architecture-neutral protocol tools for autonomous execution, sealed evaluation, and versioned improvement of medical agents.`

Recommended first tag: `v0.1.0`

## Initial GitHub setup

1. Create a public repository without generating a README, license, or `.gitignore` on GitHub.
2. Upload this directory as the repository root.
3. Confirm that GitHub Actions passes `protocol-ci`.
4. Review `docs/PUBLIC_RELEASE_BOUNDARY.md` and run `python scripts/release_boundary_check.py` before the first public commit.
5. Create tag `v0.1.0` only after the branch passes tests and the release boundary review.
6. Add the SSRN URL to `CITATION.cff` and the README after SSRN assigns the public abstract page. Do not add the paper manuscript itself to the protocol repository unless a separate publication policy explicitly calls for it.

The public repository is a protocol and evidence toolkit. Hidden evaluation materials and participant systems remain separately controlled.
