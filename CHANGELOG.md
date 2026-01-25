# CHANGELOG

<!-- version list -->

## v1.2.1 (2026-01-02)

*January 24, 2026*

- feat: Complete removal of legacy GUI and UI-related dependencies
- feat: Backend refactored into a pure service-oriented API (API-first architecture)
- feat: Unified API response contract using a standard { success, data, error } schema
- feat: Automatic bootstrap process executed at application startup
- feat: Automatic generation of SSL certificates when missing
- feat: Automatic creation of default admin user (idempotent)
- feat: Centralized password hashing using Argon2 via PasswordHasher
- feat: Full IAM (Identity & Access Management) exposed via API endpoints
- feat: Runtime control via API endpoints (/server/start, /server/stop)
- feat: Centralized runtime guard using before_request pipeline
- feat: Explicit allowlist for runtime-disabled mode
- feat: OData endpoints isolated from core API response contract
- feat: Support for OData query parameters ($select, $filter, $top, $skip, $orderby)
- feat: Complete Postman collection covering all current endpoints
- feat: Modular project structure prepared for React frontend integration
- feat: Clean separation between API, runtime control, IAM, and OData layers

- fix: Resolved deadlock preventing /server/start from being called when runtime was stopped
- fix: Removed misuse of abort() causing HTML responses and breaking API contract
- fix: Fixed inconsistent runtime state handling (server_state.running vs SERVER_STATE)
- fix: Corrected invalid item count calculation (len("items"))
- fix: Fixed bootstrap flow when admin user did not exist (get_user() exception handling)
- fix: Removed duplicated and hardcoded configuration access across modules
- fix: Eliminated mixed responsibilities between API routes and infrastructure logic
- fix: Removed unused and legacy code paths related to embedded server startup
- fix: Fixed inconsistent error handling across IAM endpoints
- fix: Ensured OData endpoints always return JSON responses
- fix: Removed HTML rendering from API Blueprint
- fix: Removed obsolete server lifecycle controller and orphaned scripts


*January 4, 2026*

- Added
  - Integrated SQLite-backed IAM permission checks
  - Enforced user and group-based authorization on OData endpoints
  - Added runtime access validation using JWT identity
  - SQLite-based IAM persistence layer
  - Admin API for managing users, groups, endpoints and permissions
  - Full CRUD operations using JSON payloads
  - Group-user relationship management
  - Permission policies for users and groups
  - Postman collection for end-to-end IAM testing


*January 3, 2026*

- Added
  - Logical API namespaces (/odata/<namespace>/<endpoint>).
  - Endpoint-to-source mapping via configuration (no table names exposed).
  - Permission checks per endpoint and action (read / write).

- Changed
  - OData routing now resolves logical endpoints instead of physical tables.

- Fixed
  - Incorrect endpoint resolution and duplicated query results.
  - Case-sensitivity issues in table name matching.


### Features

*January 2, 2026*
- System-Native Logging
  - Linux: syslog / journald
  - Windows: Event Viewer
- Structured Error Tracking
- Performance & Privacy First
- Anonymous Usage Analytics
  - Self-Cleaning Telemetry State
- Refactoring to catch errors during execution
([`25c1a42`](https://github.com/crcarreno/PulseConnector/commit/50e0eebd1062ac8bdf7f503c9bca697436b8c549))

## v1.2.0 (2025-12-29)

### Bug Fixes

- Correct semantic-release config for version.py update
  ([`3b2d598`](https://github.com/crcarreno/PulseConnector/commit/3b2d5982b51a9c07d4e7b71a7e4870c7d4eb3969))

### Features

- Correct semantic-release config and sync version
  ([`b1d245a`](https://github.com/crcarreno/PulseConnector/commit/b1d245a20557487671a017681d87e73ee40b426a))


## v1.1.1 (2025-12-29)

### Bug Fixes

- Correct semantic-release config for version.py update
  ([`3b2d598`](https://github.com/crcarreno/PulseConnector/commit/3b2d5982b51a9c07d4e7b71a7e4870c7d4eb3969))


## v1.1.0 (2025-12-29)

### Continuous Integration

- Add semantic-release automation
  ([`9215dc7`](https://github.com/crcarreno/PulseConnector/commit/9215dc7d6cef31aef0182d687b4b9b195d735ebf))

### Features

- Add public /version endpoint for auto-updater
  ([`24895b7`](https://github.com/crcarreno/PulseConnector/commit/24895b7ae6d8f19b9b7fb597d66b3d2868ccee47))


## v1.0.0 (2025-12-28)

- Initial Release
