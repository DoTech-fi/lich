.PHONY: install-vault-hook

## Vault sync — install post-commit hook that updates the Obsidian knowledge base
install-vault-hook:
	@bash ~/.vault-sync/install-hook.sh
