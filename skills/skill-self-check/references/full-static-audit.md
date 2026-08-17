# Full Static Audit

Read this reference only when the user explicitly requests the complete
installed check pack or asks to save all source reports.

Run the bundled read-only runner:

```bash
python scripts/run_full_audit.py /absolute/path/to/target-skill \
  --out-dir /private/path/target-skill-audit \
  --work-package /absolute/path/to/work-package \
  --pretty
```

- The runner always executes `hard_gates.py` and `skill-ship-safety`.
- Supply `--work-package` only when `agent-work-readiness` evidence is needed.
- The runner emits JSON only; it does not generate a maturity profile or HTML.
- Store real reports outside the audited Skill and its source repository.
- Verify the target fingerprint is unchanged.

Use [../REPORT-TEMPLATE.md](../REPORT-TEMPLATE.md) only when the user also asks
for a deep/full technical report.

Done when source JSON is saved in an allowed location, the target fingerprint
is unchanged, and missing optional checks are reported without changing the
core gate.
