import os
import json
from dotenv import load_dotenv
from google.cloud import firestore
from google.oauth2 import service_account
from app.schemas import ChatTurn

load_dotenv()


def _get_client():
    creds_json = os.environ.get("FIREBASE_CREDENTIALS_JSON")
    if creds_json:
        creds_dict = json.loads(creds_json)
        credentials = service_account.Credentials.from_service_account_info(creds_dict)
        return firestore.Client(credentials=credentials, project=creds_dict["project_id"])
    return firestore.Client()


db = _get_client()


def append_turn(session_id: str, role: str, content: str, intent: str = None) -> None:
    turn = ChatTurn(role=role, content=content, intent=intent)
    db.collection("sessions").document(session_id).collection("turns").add({
        **turn.model_dump(),
        "timestamp": firestore.SERVER_TIMESTAMP,
    })


def get_history(session_id: str, limit: int = 10) -> list[ChatTurn]:
    docs = (
        db.collection("sessions")
        .document(session_id)
        .collection("turns")
        .order_by("timestamp")
        .limit_to_last(limit)
        .get()
    )
    turns = []
    for doc in docs:
        data = doc.to_dict()
        data.pop("timestamp", None)
        turns.append(ChatTurn(**data))
    return turns
