# Tgether SDK

The tgether sdk is a set of common functions used when interacting with the tgether PoS payment system.

## Initialize

1. install (uv)[https://docs.astral.sh/uv/getting-started/installation/]
2. run `uv venv` # sets up venv
3. run `uv pip install .` # isntalls dependencies

Running Tests:

1. run `uv run pytest`


# Signatures

- Tgether uses a (EIP-712)[https://blog.solichain.com/eip-712-simplified-enhancing-data-hashing-and-signing-0b642242b69a] signatures to allow payers to submit orders on behalf of vendors
- By signing these order auth messages off chain we can pass the gas cost of creating an order onto the user without risking the integrity of setting prices and order ids.