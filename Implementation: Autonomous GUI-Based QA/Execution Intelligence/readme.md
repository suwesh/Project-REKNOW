# Execution Intelligence

Representative implementation artifacts for the Project REKNOW
Autonomous GUI-Based QA execution subsystem.

## Structure

```text
Execution Intelligence/
├── readme.md
├── windows-runtime/
│   ├── readme.md
│   ├── mr_tester.py
│   ├── personas.json
│   ├── test_execution_plan.json
│   └── tools/
└── wsl-perception-service/
    └── eyes_of_gui_qa.py
```

## Components

- `windows-runtime/`: Windows-side execution controller, multimodal intent selection, deterministic target resolution, GUI actuation, screen-state storage, validation, and evidence compilation.
- `wsl-perception-service/eyes_of_gui_qa.py`: FastAPI-based GPU perception service that detects GUI regions, applies OCR to detected regions, generates a structured UI map, and saves an annotated debug image. It uses <a href="https://huggingface.co/Salesforce/GPA-GUI-Detector">huggingface.co/Salesforce/GPA-GUI-Detector</a> to detect GUI-element bounding boxes and <a href="https://huggingface.co/microsoft/trocr-base-printed">huggingface.co/microsoft/trocr-base-printed</a> to extract visible text from each detected region. The service returns element IDs, detected text, center coordinates, and bounding boxes as a structured UI map, while also saving an annotated debug image.
