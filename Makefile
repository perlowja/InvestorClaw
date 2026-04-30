# InvestorClaw — release build targets
.PHONY: skill-bundle audit-check clean help

VERSION := $(shell grep -E '^version\s*=' pyproject.toml | head -1 | sed 's/.*"\(.*\)".*/\1/')
BUNDLE_NAME := investorclaw-skill-$(VERSION)
BUNDLE_TARBALL := build/$(BUNDLE_NAME).tar.gz

help:
	@echo "InvestorClaw — release build targets"
	@echo ""
	@echo "  make audit-check   — verify SKILL.md/COMMANDS.md/CAPABILITIES.md pass zeroclaw audit"
	@echo "  make skill-bundle  — build $(BUNDLE_TARBALL) (audit + whitelist + tar)"
	@echo "  make clean         — remove dist/"
	@echo ""
	@echo "Current version: $(VERSION)"

audit-check:
	@python3 -c 'import sys; sys.path.insert(0, "scripts"); from build_skill_bundle import audit_markdown_content; v = audit_markdown_content(); print("violations:", len(v)); [print(f"  {f}:{l} {p}") for f,l,p in v]; sys.exit(1 if v else 0)'

skill-bundle:
	@python3 scripts/build_skill_bundle.py

clean:
	@rm -rf build/
	@echo "Cleaned build/"
