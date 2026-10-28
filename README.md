# .github

Organisation-level files for [github.com/uniqaiapp](https://github.com/uniqaiapp).

| Path | What GitHub does with it |
|:---|:---|
| `profile/README.md` | Rendered on the organisation page. The repository showcase and the install block live there. |
| `profile/assets/banner.svg`, `banner-light.svg` | Animated header for the profile README (CSS keyframes only, honours `prefers-reduced-motion`). |
| `SECURITY.md` | Default security policy for every repository in the organisation that does not ship its own. |
| `CODE_OF_CONDUCT.md` | Default code of conduct, same rule. |
| `scripts/check.py` | Stdlib-only checks for this repository: brand-only strings, UTM on every link to uniqai.app, well-formed banners, and (with `--repos`) that the showcase matches the repository list. |

Run the checks with `python3 scripts/check.py`. Nothing to install.

Maintained by UniqAI, support@uniqai.app. MIT, see `LICENSE`.
