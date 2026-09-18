# GitHub Release Checklist

1. Run the unit tests.
2. Run the release-boundary scanner.
3. Confirm the repository contains no hidden cases, gold values, scorer implementation, answer-bearing fixtures, official solution, or comparator implementation material.
4. Review the complete Git history and release archive, not only the current working tree.
5. Confirm that the example remains mechanical and cannot solve substantive tasks.
6. Confirm all public schemas use stable identifiers and declare their protocol version.
7. Confirm a scored-obligation change increments the major version.
8. Generate the source archive from a clean tag.
9. Record the tag, commit digest, archive digest, and release date.
10. Publish a contamination advisory and retire affected sealed sets if prohibited material is later discovered.
