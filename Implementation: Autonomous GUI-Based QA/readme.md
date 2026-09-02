# Autonomous GUI-Based QA Reference Implementation

Sanitized implementation artifacts for the Project REKNOW proof of concept.<br>
The implementation is divided into three cooperating subsystems:

## Components

- `./Business Intelligence/`: Power Automate workflows and AI Builder prompts for work intake, requirement analysis, business-level planning, and plan acknowledgment.
- `./State and Artifact Bridge/`: Microsoft Graph-based artifact access, document extraction, run-state polling, state-specific handler dispatch, domain-knowledge integration, and duplicate-processing prevention.
- `./Execution Intelligence/`: Windows/WSL execution subsystem for GUI perception, semantic intent selection, deterministic target resolution, GUI actuation, validation, and evidence capture.
