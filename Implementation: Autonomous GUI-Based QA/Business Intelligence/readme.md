<img width="1716" height="1747" alt="reknow-business-intelligence-flows" src="https://github.com/user-attachments/assets/40eb486f-2ae7-4e28-a4e1-b034c5653c0f" /><br>

The `Work Intake Workflows` created the following subfolders in the `qa_root/run-folder-id/` SharePoint folder:<br>
```text
[
  "00_Metadata",
  "01_Input",
  "02_Analysis",
  "03_Planning",
  "04_Execution",
  "05_Evidence",
  "06_Status"
]
```

## AI Builder Prompts
- `QA Analyst.txt`: identifies intent, baseline workflows, and retrieval requirements -> in `Analysis Workflows`.
- `QA Planner.txt`: produces ordered business-level goals from requirements, analysis, and retrieved context -> in `Planning Workflows`.
- `QA draft email acknowledgment for test request with plan.txt`: generates the same-thread plan acknowledgment -> in `Plan Acknowledgment Workflows`.
