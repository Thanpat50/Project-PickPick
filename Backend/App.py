import json
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse

app = FastAPI()


with open("cases.json", "r", encoding="utf-8") as f:
    cases_data = json.load(f)


app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def index():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.get("/cases")
async def get_cases():

    case_names = [c["case"] for c in cases_data.get("cases", [])]
    return {"cases": case_names}


@app.post("/start")
async def start_case(data: dict):

    case_name = data.get("case")
    case = next((c for c in cases_data["cases"] if c["case"] == case_name), None)
    if not case:
        return JSONResponse(status_code=404, content={"error": "Case not found"})

    branches = case.get("branches", [])
    if len(branches) > 1:

        branch_titles = []
        for b in branches:
            title = b.get("branch") or b.get("question") or "หัวข้อ"
            branch_titles.append(title)
        return {"branches": branch_titles}
    elif len(branches) == 1:

        branch = branches[0]
        return {"first_question": branch}
    else:
        return JSONResponse(status_code=400, content={"error": "No branches found"})


@app.post("/select_branch")
async def select_branch(data: dict):
    case_name = data.get("case")
    branch_idx = data.get("branch_index")
    case = next((c for c in cases_data["cases"] if c["case"] == case_name), None)
    if not case:
        return JSONResponse(status_code=404, content={"error": "Case not found"})

    branches = case.get("branches", [])
    if branch_idx is None or branch_idx < 0 or branch_idx >= len(branches):
        return JSONResponse(status_code=400, content={"error": "Invalid branch index"})

    branch = branches[branch_idx]

    if "question" in branch:
        return {"first_question": branch}


    if "next_questions" in branch:
        return {"first_question": branch["next_questions"][0]}
    if "next_question" in branch:
        return {"first_question": branch["next_question"]}

    if "options" in branch:
        return {"first_question": {
            "question": branch.get("branch", "คำถามต่อไป"),
            "options": branch["options"]
        }}

    return JSONResponse(status_code=400, content={"error": "No question found in selected branch"})



@app.post("/next_question")
async def next_question(data: dict):
    question = data.get("question")
    selected_option_index = data.get("selected_option_index")

    if question is None or selected_option_index is None:
        return JSONResponse(status_code=400, content={"error": "Missing data"})

    options = question.get("options", [])
    if selected_option_index < 0 or selected_option_index >= len(options):
        return JSONResponse(status_code=400, content={"error": "Invalid option index"})

    selected = options[selected_option_index]

    note = selected.get("note")
    response = {"note": note}

    if "result" in selected:
        response["result"] = selected["result"]
        response["finished"] = True
        return response


    if "next_question" in selected:
        response["next_questions"] = [selected["next_question"]]
        response["finished"] = False
        return response

    if "next_questions" in selected:
        response["next_questions"] = selected["next_questions"]
        response["finished"] = False
        return response

    if "sub_questions" in selected:
        response["next_questions"] = selected["sub_questions"]
        response["finished"] = False
        return response

    if "follow_ups" in selected:
        response["next_questions"] = selected["follow_ups"]
        response["finished"] = False
        return response


    response["finished"] = True
    return response
