# TT Personal Life Assistant Team

## Background
This project is to build a personal life assistant team consisting of 5 AI assistant roles. These assistants will act as my intelligent avatars, helping me manage daily life, improve efficiency, and enhance self-awareness.


## Architecture Overview
* Modular assistants implemented as independent MCP-style servers (see scripts/ and agent files in .claude/agents/).
* Templates in templates/ generate final markdown documents saved under daily_logs/[YYYY/MM]/.
* Personal context lives in aboutme/ and is used to personalize outputs.
Sensitive keys live in config/.env. See CLAUDE.md for environment configuration.

## Development & Extensibility
* Add a new assistant: update conception.md design, create a template in templates/, add agent config to .claude/agents/, and register the server in run_server.py.
* File operations and report generation follow the file management conventions described in conception.md and daily_logs/README.md.
* Use the provided templates to keep output consistent and machine-parseable.


## Testing & Deployment
* Configure environment in config/.env (required keys documented in CLAUDE.md).
* Use scripts/servers/test_servers.py for integration tests; run the MCP servers locally for manual testing.