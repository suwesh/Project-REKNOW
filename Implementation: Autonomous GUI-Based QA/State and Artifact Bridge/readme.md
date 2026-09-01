# State and Artifact Bridge
Representative implementation artifacts for the server-side coordination layer of the Project REKNOW proof of concept.

## Components
• `ms_graph_api_auth.py`: Microsoft Graph authentication<br>
• `ms_graph_api_utils.py`: SharePoint run folder artifact access, document extraction, and upload utilities<br>
• `ms_graph_api_handlers.py`: state-specific handlers<br>
• `ms_graph_api_poller.py`: run-state polling and duplicate-processing prevention<br>
• `msgraph_apikeys.json`: empty credential template<br>
• `poller_service.py`: service entry point and graceful shutdown handling<br>
• `qa_root_processedruns.json`: sanitized example of processed-state tracking. The deployed version was stored under `/opt/`.<br>
• `qaroot-poller.service`: representative systemd service configuration<br>

## External Dependency
• The `search_domain_knowledge()` function inside `ms_graph_api_handlers.py` represents the existing external domain-knowledge retrieval system used by the proof of concept. Its underlying enterprise knowledge base and retrieval implementation are not included in this repository.<br>
• `your_app.RAG_RESOURCES` represents the retrieval indexes, metadata, and other resources loaded by the host application.<br>
These external enterprise components are not included in this repository.

## Implemented States
• `RECEIVED`<br>
• `ANALYZED`<br>
• `PLANNED`<br>
The transition from the planning stage to desktop execution remained a manual handoff in the demonstrated prototype.

## Note
These files are sanitized implementation artifacts intended to document the proof-of-concept architecture. They are not distributed as a standalone deployable application.
