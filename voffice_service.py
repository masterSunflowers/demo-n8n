from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn


app = FastAPI()

# CORS configuration
origins = [
    "http://localhost:5678",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Welcome to the VOffice Service"}


@app.get("/api/v1/voffice/getListMeetings")
async def get_list_meetings():
    # Simulated response for the list of meetings
    meetings = [
        {
            "meeting_id": 1,
            "title": "Project Kickoff",
            "date": "2023-10-01",
            "time": "10:00 AM",
            "participants": ["Alice", "Bob"],
        },
        {
            "meeting_id": 2,
            "title": "Weekly Sync",
            "date": "2023-10-02",
            "time": "2:00 PM",
            "participants": ["Charlie", "David"],
        },
    ]
    return {"meetings": meetings}


@app.get("/api/v1/voffice/getListDocuments")
async def get_list_documents():
    # Simulated response for the list of documents
    documents = [
        {
            "document_id": 1,
            "title": "Project Plan",
            "uploaded_by": "Alice",
            "upload_date": "2023-09-25",
        },
        {
            "document_id": 2,
            "title": "Weekly Report",
            "uploaded_by": "Bob",
            "upload_date": "2023-09-26",
        },
    ]
    return {"documents": documents}


def main():
    uvicorn.run("voffice_service:app", host="localhost", port=8000, reload=True)


if __name__ == "__main__":
    main()
