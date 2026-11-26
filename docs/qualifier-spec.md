# Version Qualifier Validation Specification

## 1. Objective

This document defines how version tags with **qualifiers** are to be interpreted, validated, and compared by the `version-tag-check` GitHub Action.

The goals are:

- To support version tags that extend semantic versioning with qualifiers.
- To restrict qualifiers to a small, well-defined set with clear patterns.
- To define precedence (ordering) rules between versions with and without qualifiers.
- To clarify how sequences of tags are validated for monotonic increase.

This specification is **business/functional** and does not prescribe implementation details.

Related issues:

- [#5 – Add support for qualifiers and their validation](https://github.com/AbsaOSS/version-tag-check/issues/5)
- [#38 – Spike: Integrate new version qualifier validation spec into repo documentation and workflow](https://github.com/AbsaOSS/version-tag-check/issues/38)
- [#119 – Accept the PEP 440 release candidate tag `vX.Y.ZrcN`](https://github.com/AbsaOSS/version-tag-check/issues/119)

---

## 2. Supported Version Format

### 2.1 Base version

The base version follows the standard semantic pattern:

- `Major.Minor.Patch`

Where each of `Major`, `Minor`, and `Patch` is a non-negative integer.

Examples:

- `1.0.0`
- `2.3.5`
- `10.0.12`

### 2.2 Optional qualifier

Versions may include a single, optional **qualifier** appended with a hyphen:

- `Major.Minor.Patch[-qualifier]`

Rules:

- The hyphen `-` introduces the qualifier. The one exception is the PEP 440 release candidate (section 2.3).
- At most **one** qualifier is allowed.
- No additional segments after the qualifier are allowed.

Examples of **valid shapes** (ignoring whether the qualifier itself is allowed):

- `1.0.0-ALPHA`
- `1.0.0-RC1`
- `1.0.1-HF2`

Examples of **invalid shapes**:

- `1.0.0-ALPHA-RC1`
- `1.0.0-ALPHA.1`
- `1.0.0-` (no qualifier after hyphen)

### 2.3 PEP 440 release candidate

A release candidate may also be written in the normalised spelling of
[PEP 440](https://peps.python.org/pep-0440/):

- `Major.Minor.PatchrcN`

Rationale:

- PEP 440 is the version standard of Python packaging. It normalises every pre-release to lowercase with no separator,
  so a package versioned `0.9.0-RC1` is built, published and installed as `0.9.0rc1`. pip, PyPI, the wheel file name
  and `importlib.metadata.version()` all show `0.9.0rc1`.
- A repository whose tag is `v` plus its package version therefore cannot keep `-RC1`. Accepting the normalised
  spelling lets it tag each release in the one spelling it publishes.

Rules:

- Only the normalised spelling is allowed: lowercase `rc`, no separator, no leading zero in `N`.
- `N` is `1`–`99`, the range of `RCx` (section 3.4). PEP 440 also allows `rc0`; it is excluded.
- `Major.Minor.PatchrcN` is the RC qualifier written another way, not a new qualifier. It normalises to
  `Major.Minor.Patch-RCN`: the two spellings are one release, equal in precedence (section 4.2) and in presence
  checks, so a release cannot be tagged in both.
- No other PEP 440 segment is supported (section 7).

Examples:

- Valid: `0.9.0rc1`, `0.9.0rc2`, `0.9.0rc99`
- Invalid: `0.9.0rc0`, `0.9.0rc100`, `0.9.0rc01`, `0.9.0rc`, `0.9.0-rc1`, `0.9.0.rc1`, `0.9.0_rc1`, `0.9.0RC1`,
  `0.9.0c1`, `0.9.0pre1`, `0.9.0rc1-SNAPSHOT`

---

## 3. Allowed Qualifiers and Patterns

Only the following qualifiers are allowed. Qualifiers are case-sensitive and must appear in **uppercase** exactly as described here. The PEP 440 release candidate `rcN` (section 2.3) is the one lowercase spelling; it is the RC qualifier, not a separate one.

### 3.1 SNAPSHOT

- Literal: `SNAPSHOT`
- Pattern: exactly `SNAPSHOT`

Examples:

- Valid: `1.0.0-SNAPSHOT`
- Invalid: `1.0.0-snapshot`, `1.0.0-SNAPSHOT1`

### 3.2 ALPHA

- Literal: `ALPHA`
- Pattern: exactly `ALPHA`

Examples:

- Valid: `1.0.0-ALPHA`
- Invalid: `1.0.0-alpha`, `1.0.0-ALPHA1`

### 3.3 BETA

- Literal: `BETA`
- Pattern: exactly `BETA`

Examples:

- Valid: `1.0.0-BETA`
- Invalid: `1.0.0-beta`, `1.0.0-BETA2`

### 3.4 Release Candidate (RC)

- Prefix: `RC`
- Numeric suffix: 1–2 digits (`1`–`99`)
- Overall pattern: `RC[0-9]{1,2}`

Examples:

- Valid: `1.0.0-RC1`, `1.0.0-RC2`, `1.0.0-RC10`
- Invalid: `1.0.0-RC`, `1.0.0-RC001`, `1.0.0-Rc1`, `1.0.0-rc1`

The same release candidate may be written `1.0.0rc1` (section 2.3).

### 3.5 RELEASE

- Literal: `RELEASE`
- Pattern: exactly `RELEASE`

Examples:

- Valid: `1.0.0-RELEASE`
- Invalid: `1.0.0-release`, `1.0.0-RELEASE1`

> Note: `1.0.0-RELEASE` is distinct from `1.0.0` (no qualifier). Both are “final-like” states but have different precedence.

### 3.6 HOTFIX (HF)

- Prefix: `HF`
- Numeric suffix: 1–2 digits (`1`–`99`)
- Overall pattern: `HF[0-9]{1,2}`

Examples:

- Valid: `1.0.1-HF1`, `1.0.1-HF2`, `1.0.1-HF10`
- Invalid: `1.0.1-HF`, `1.0.1-HF001`, `1.0.1-hf1`

---

## 4. Version Precedence Rules

### 4.1 Numeric precedence

Versions are compared first by their numeric components:

1. `Major`
2. `Minor`
3. `Patch`

Qualifiers are only considered if the numeric components are equal.

Examples:

- `2.0.0-SNAPSHOT` > `1.9.9-RELEASE`
- `1.1.0-ALPHA` > `1.0.5-HF2`

### 4.2 Qualifier precedence for the same numeric version

For the same `Major.Minor.Patch`, qualifier precedence is:

1. `SNAPSHOT` (lowest)
2. `ALPHA`
3. `BETA`
4. `RCx` (ordered by `x`)
5. `RELEASE`
6. No qualifier (highest for that numeric base)

Formally, for version `v = Major.Minor.Patch`:

- `v-SNAPSHOT` < `v-ALPHA` < `v-BETA`
- `v-BETA` < `v-RC1` < `v-RC2` < … < `v-RC99`
- `vrcN` = `v-RCN` (section 2.3), so `v-RC1` < `vrc2` < `v-RC3`
- Any `v-RC*` < `v-RELEASE`
- `v-RELEASE` < `v`

Example ordering:

- `1.0.0-SNAPSHOT`
- `1.0.0-ALPHA`
- `1.0.0-BETA`
- `1.0.0-RC1`
- `1.0.0-RC2`
- `1.0.0-RELEASE`
- `1.0.0`

### 4.3 Hotfix precedence (HF)

For the same `Major.Minor.Patch`, hotfix qualifiers are ordered by their numeric suffix:

- `v-HF1` < `v-HF2` < `v-HF10`

For comparisons with the bare version:

- A hotfix is considered a more advanced state than the same numeric version without `HF`:

  - `1.0.1` < `1.0.1-HF1` < `1.0.1-HF2`

---

## 5. Validation Rules

### 5.1 Validating a single tag

A tag is **valid** if:

1. It matches the `Major.Minor.Patch`, `Major.Minor.Patch-QUALIFIER` or `Major.Minor.PatchrcN` (section 2.3) structure, and
2. If a qualifier is present, it matches one of the allowed patterns defined in this spec.

### 5.2 Invalid qualifiers

A tag is **invalid** if:

- The qualifier is not in the allowed set (`SNAPSHOT`, `ALPHA`, `BETA`, `RC[0-9]{1,2}`, `RELEASE`, `HF[0-9]{1,2}`).
- The qualifier uses incorrect casing (e.g. `alpha`, `Rc1`).
- The qualifier pattern is malformed (e.g. `RC`, `RC001`, `HF001`).
- Multiple qualifiers or additional segments are present (e.g. `1.0.0-RC1-SNAPSHOT`).
- A release candidate uses a PEP 440 spelling other than the normalised `rcN`, or `rc0` (e.g. `1.0.0-rc1`,
  `1.0.0.rc1`, `1.0.0RC1`, `1.0.0c1`, `1.0.0rc0`).

Invalid tags should be rejected with clear error messages indicating:

- Which tag is invalid.
- Whether the problem is in the structure or the qualifier.

---

## 6. Sequence Validation (Monotonicity)

The action may validate **sequences** of tags (for example, tags over time).

A sequence is considered **monotonically increasing** if, for each consecutive pair:

- `current` is greater than (or, depending on configuration, equal to) `previous`,
- using the numeric + qualifier precedence rules defined in this document.

### 6.1 Examples of valid sequences

Examples assuming strictly increasing order:

- Pre-release progression:

  - `1.0.0-SNAPSHOT`
  - `1.0.0-ALPHA`
  - `1.0.0-BETA`
  - `1.0.0-RC1`
  - `1.0.0-RC2`
  - `1.0.0-RELEASE`
  - `1.0.0`

- Across minor versions:

  - `1.0.0-ALPHA`
  - `1.0.0-BETA`
  - `1.0.0`
  - `1.1.0-SNAPSHOT`
  - `1.1.0-RC1`
  - `1.1.0-RELEASE`
  - `1.1.0`

- With hotfixes:

  - `1.0.0-RELEASE`
  - `1.0.0`
  - `1.0.1`
  - `1.0.1-HF1`
  - `1.0.1-HF2`

- With PEP 440 release candidates, alone or mixed with `-RCx`:

  - `0.8.1`
  - `0.9.0rc1`
  - `0.9.0-RC2`
  - `0.9.0rc3`
  - `0.9.0`

### 6.2 Examples of invalid sequences

- Backwards in qualifier precedence:

  - `1.0.0-RC2`
  - `1.0.0-RC1` (invalid: RC1 < RC2)

- Backwards in numeric version:

  - `1.1.0-SNAPSHOT`
  - `1.0.1-RELEASE` (invalid: 1.0.1 < 1.1.0)

- Invalid qualifier in the middle:

  - `1.0.0-ALPHA`
  - `1.0.0-BETA1` (invalid: `BETA1` qualifier not allowed)

- Regressing from final to pre-release for same numeric version:

  - `1.0.0`
  - `1.0.0-RELEASE` (invalid: `1.0.0-RELEASE` < `1.0.0`)

- The same release candidate in the other spelling:

  - `0.9.0-RC1`
  - `0.9.0rc1` (invalid: `0.9.0rc1` = `0.9.0-RC1`)

---

## 7. Non-Goals / Exclusions

The following are explicitly **out of scope**:

- Combined qualifiers (e.g. `1.0.0-RC1-SNAPSHOT`, `1.0.0-BETA-HF1`).
- Arbitrary/custom qualifiers beyond the allowed set.
- Pre-release or build metadata segments (e.g. `1.0.0-RC1+build.123`, `1.0.0-ALPHA.1`).
- Multi-part numeric qualifiers (e.g. `RC1.1`, `HF1.2`).
- Changing semantics for versions **without** qualifiers (`Major.Minor.Patch`).
- PEP 440 beyond the release candidate of section 2.3: alpha (`aN`), beta (`bN`), development (`.devN`),
  post-release (`.postN`) and local (`+local`) segments, and the spellings PEP 440 normalises away (`-rc1`, `.rc1`,
  `c1`, `pre1`, uppercase).

---

## 8. Future Configuration Considerations

Potential future options (not required for initial implementation):

1. **Configurable allowed qualifiers**

   - Enable or disable specific qualifiers (e.g. disallow `SNAPSHOT` on main branch).

2. **Case-sensitivity settings**

   - Make qualifier matching case-insensitive and normalize to uppercase.

3. **Strict vs lenient sequence rules**

   - Strict: sequences must strictly increase.
   - Lenient: allow equal versions (e.g. re-tagging).

4. **Hotfix semantics**

   - Ability to configure how hotfix tags relate to non-hotfix versions.

5. **Custom precedence**

   - Override default order `SNAPSHOT < ALPHA < BETA < RC < RELEASE < no qualifier`.

---

## 9. Acceptance Criteria (Spec)

The specification is considered adopted when:

- It is present in the repository (e.g. `docs/qualifier-spec.md`).
- It is discoverable from main documentation (e.g. linked from `README.md`).
- It clearly documents:
  - Allowed formats and qualifiers.
  - Precedence rules.
  - Validation and sequence rules.
  - Non-goals and future configuration considerations.

Implementation and testing of these rules in code can be tracked in separate issues.
