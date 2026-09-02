# Windows Runtime

Representative Windows-side implementation artifacts for the Autonomous GUI-Based QA execution subsystem.

## Files
```text
windows-runtime/
├── mr_tester.py
├── personas.json
├── test_execution_plan.json
└── tools/
    ├── actor.py
    ├── gui_actions.py
    ├── operator_utils.py
    ├── percept_gui.py
    └── screenshots_compiler.py
```

## Components

- `mr_tester.py`: main execution controller for iterating through business-level goals, invoking perception, selecting semantic actions, executing GUI operations, and calling validation components.
- `personas.json`: system prompts for the semantic action agent, Atomic Execution Critic, and Business Step Judge.
- `test_execution_plan.json`: template for the ordered business-level goals consumed by the execution controller.
- `tools/screenshots_compiler.py`: compiles ordered execution screenshots into an MP4 replay.
- `tools/actor.py`: resolves semantic target text against the UI map and converts the selected intent into an executable GUI action.
- `tools/gui_actions.py`: screenshot capture and low-level PyAutoGUI primitives for clicking, typing, key presses, and scrolling.
- `tools/operator_utils.py`: LM Studio multimodal API client, image encoding, and persona-loading utilities.
- `tools/percept_gui.py`: client for the WSL perception service and utilities for preserving and retrieving screen-state screenshots.
