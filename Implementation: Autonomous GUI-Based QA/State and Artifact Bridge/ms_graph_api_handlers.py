import json
from your_domain_knowledge_retreival import search_domain_knowledge # replace with your actual domain knowledge retrieval function
from ms_graph_api_utils import list_runfolder_files, download_file_content, extract_pdf_text, extract_docx_text, upload_concated_inputtext_file, upload_plannerinput_file
# functions that execute after power automate runs state changes
def process_automation_run_state_change(run_folder, state_data, rag_resources):
    state = state_data.get("state")
    if not state:
        print(f"[{run_folder}] Missing state")
        return  # soft exit
    # finite state machine mapping
    handlers = {
        "RECEIVED": handle_received_state,
        "ANALYZED": handle_analyzed_state,
        "PLANNED": handle_planned_state,
        "EXECUTED": None
    }
    handler = handlers.get(state)
    if not handler:
        print(f"[{run_folder}] Unknown state: {state}")
        return  # soft exit
    handler(run_folder, state_data, rag_resources)# handler will be one of the below handle_<state> function and that function will be executed by this line

def handle_received_state(run_folder, state_data, rag_resources):
    #1. get the po email + brd + fsd attachments saved by power automate inside 01_Input subfolder
    #2. save the concatenated file into a text file in subfolder 02_Analysis/analyst_input_concatenated.txt
    # list files in 01_Input subfolder
    input_files = list_runfolder_files(run_folder, "01_Input")
    po_email_text = ""
    attachment_texts = []
    for file in input_files:
        name = file.get("name")
        item_id = file.get("id")
        if not name or not item_id:
            continue
        binary = download_file_content(item_id)
        if name.lower() == "po_email.txt":
            po_email_text = binary.decode("utf-8", errors="ignore")
        elif name.lower().endswith(".pdf"):
            attachment_texts.append(
                f"\n--- {name} ---\n{extract_pdf_text(binary)}"
            )
        elif name.lower().endswith(".docx"):
            attachment_texts.append(
                f"\n--- {name} ---\n{extract_docx_text(binary)}"
            )
    final_content = (
        "=== PO EMAIL ===\n" + po_email_text + 
        "\n\n=== ATTACHMENTS ===\n" + "\n\n".join(attachment_texts)
    )
    upload_concated_inputtext_file(run_folder, final_content)
    print(f"[{run_folder}] analyst_input_concatenated.txt written")
def handle_analyzed_state(run_folder, state_data, rag_resources):
    #1. get the 02_Analysis/analyst_ragsearch_queries.txt
    #2. do faiss vector search using queries from analyst_ragsearch_queries.txt json structure text and save the rag contents as input context file for planner
    # list files in 02_Analysis subfolder
    input_files = list_runfolder_files(run_folder, "02_Analysis")
    for file in input_files:
        name = file.get("name")
        if name.lower() == "analyst_ragsearch_queries.txt":
            item_id = file.get("id")
            binary = download_file_content(item_id)
            text = binary.decode("utf-8", errors="ignore")
            parsed = json.loads(text)
            retrieval_queries = [item["query"] for item in parsed.get("retrieval_queries", [])]
        else: continue
    rag_results = []
    for query in retrieval_queries:# search vector knowledge base
        faqs_ctx, video_ctx, manuals_ctx, _ = search_domain_knowledge(sentences=query, rag_resources=rag_resources) # ypur actual retreival function
        rag_results.append({
            "queries": query,
            "contexts": {
                "faqs": faqs_ctx,
                "videos": video_ctx,
                "manuals": manuals_ctx
            }
        })
    rag_context = {
        "rag_context": [
            {
                "query": item["queries"],
                "faqs_context": item["contexts"]["faqs"],
                "videos_context": item["contexts"]["videos"],
                "manuals_context": item["contexts"]["manuals"],
            }
            for item in rag_results
        ]
    }
    upload_plannerinput_file(run_folder, rag_context)
    print(f"[{run_folder}] planner_input_ragcontext.txt written with {len(rag_results)} queries")
def handle_planned_state(run_folder, state_data, rag_resources):
    #1. get the 03_Planning/test_execution_plan.txt
    input_files = list_runfolder_files(run_folder, "03_Planning")
    for file in input_files:
        name = file.get("name")
        if name.lower() == "test_execution_plan.txt":
            item_id = file.get("id")
            binary = download_file_content(item_id)
            text = binary.decode("utf-8", errors="ignore")
            plan_json = json.loads(text)
            ##upload plan into 04_Execution as .json file and then have it poll cua from there
            break
    return None
