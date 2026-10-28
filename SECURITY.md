# Security policy

This policy applies to every repository under [github.com/uniqaiapp](https://github.com/uniqaiapp) that does not ship its own `SECURITY.md`.

## Scope

The scripts, skills and data in these repositories. They run locally, have no third-party dependencies, and make no network calls unless the README of that repository says so (for example, a script that sends a prompt to a model provider you configure with your own key).

Issues with the UniqAI app itself (uniqai.app, web.uniqai.app) go to the same address below.

## Reporting a vulnerability

Email **support@uniqai.app** with the subject `Security: <repository name>`. Please do not open a public issue for anything that could be exploited before it is fixed.

Include:

- the repository and version or tag (`git describe --tags` or the `CHANGELOG.md` entry);
- steps to reproduce, or the input that triggers the problem;
- what you think the impact is;
- whether you want to be credited in the changelog, and under which handle.

We acknowledge reports by email and tell you what we intend to do and roughly when. There is no bug bounty programme.

## Keys and secrets

These repositories never contain API keys, tokens or credentials; examples use placeholder environment variable names only. If you find a real credential anywhere in the history, report it as above and assume it has already been revoked.

## Supported versions

Only the latest tagged release of each repository receives fixes.
