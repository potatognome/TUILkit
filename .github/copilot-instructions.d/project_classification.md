PROJECT_CLASSIFICATION.md
(Place in copilot-instructions.d/)

Purpose
This extension defines how every project in the PrismCorp ecosystem must classify itself inside the INFO section of its primary config.
Classification ensures consistent introspection, validation, orchestration, and tooling behavior across all repositories.

1. Project Type
Every project must declare a top‑level project_type.
This identifies the project’s category within the ecosystem.

Valid values:

core — foundational standards, schemas, taxonomies

infrastructure — tools that enforce, orchestrate, scaffold, introspect

tenant — departments, applications, agents, data repositories

project_type determines dependency direction and high‑level behavior.

2. Role
Every project must declare a role, even if descriptive.
Roles describe what the project does within its type.

Core roles
foundation

schema

taxonomy

Infrastructure roles (operational)
validation

scaffolding

introspection

orchestration

ui

logging

sync

Tenant roles
department

application

data

agent

Note:  
Only infrastructure roles affect system behavior.
Core and tenant roles are descriptive for consistency and schema uniformity.

3. Interface Capabilities
Projects must declare how they can be interacted with using a boolean capability matrix under project_interfaces.

Valid interface keys:

cli

cli_args

cli_menu

cli_menu_args

cli_invisible

config_driven_cli

compositor

tui

api

service

logging_only

This matrix supports:

standard CLI

config‑driven CLI

menu systems

invisible menu backends

compositor UIs

TUIs

agent/robot APIs

background services

data‑only/logging‑only repos

4. Example INFO Block
yaml
INFO:
  project_type: "infrastructure"
  role: "validation"
  project_interfaces:
    cli: true
    cli_args: true
    cli_menu: true
    cli_menu_args: true
    cli_invisible: true
    config_driven_cli: true
    compositor: false
    tui: false
    api: true
    service: false
    logging_only: false
5. Enforcement
OrgArchitect uses project_type and role to classify projects and emit flowspec/jobspec.

V4l1d8r validates that the declared type, role, and interfaces match expected behavior.

PrismCommand uses infrastructure roles to load and orchestrate system components.

All projects must include all three fields for schema uniformity.
