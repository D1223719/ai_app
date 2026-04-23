from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from pydantic import BaseModel
import os
import shutil

from . import models, database, llm

# Create tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="AI Resume Consultant API")

# Setup upload dir
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_or_create_default_user(db: Session):
    user = db.query(models.User).filter(models.User.email == "demo@example.com").first()
    if not user:
        user = models.User(name="Demo User", email="demo@example.com")
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

class SessionCreate(BaseModel):
    title: str

class ChatMessageRequest(BaseModel):
    content: str

@app.post("/api/sessions")
def create_session(session_data: SessionCreate, db: Session = Depends(get_db)):
    user = get_or_create_default_user(db)
    db_session = models.Session(title=session_data.title, user_id=user.id)
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

@app.get("/api/sessions")
def list_sessions(db: Session = Depends(get_db)):
    user = get_or_create_default_user(db)
    return db.query(models.Session).filter(models.Session.user_id == user.id).order_by(models.Session.updated_at.desc()).all()

@app.get("/api/sessions/{session_id}/messages")
def get_messages(session_id: str, db: Session = Depends(get_db)):
    return db.query(models.Message).filter(models.Message.session_id == session_id).order_by(models.Message.created_at.asc()).all()

@app.post("/api/sessions/{session_id}/chat")
def chat(session_id: str, req: ChatMessageRequest, db: Session = Depends(get_db)):
    user_msg = models.Message(session_id=session_id, role="user", content=req.content)
    db.add(user_msg)
    db.commit()

    history = db.query(models.Message).filter(models.Message.session_id == session_id).order_by(models.Message.created_at.asc()).all()
    history_dicts = [{"role": m.role, "content": m.content} for m in history]

    try:
        assistant_reply = llm.generate_chat_response(history_dicts)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    ast_msg = models.Message(session_id=session_id, role="assistant", content=assistant_reply)
    db.add(ast_msg)
    
    # Update session modified time
    session = db.query(models.Session).filter(models.Session.id == session_id).first()
    if session:
        session.updated_at = ast_msg.created_at
    
    db.commit()

    return {"user_message": user_msg, "assistant_message": ast_msg}

@app.post("/api/sessions/{session_id}/regenerate")
def regenerate_chat(session_id: str, db: Session = Depends(get_db)):
    # 1. Find the last message
    last_msg = db.query(models.Message).filter(models.Message.session_id == session_id).order_by(models.Message.created_at.desc()).first()
    
    if not last_msg:
        raise HTTPException(status_code=400, detail="No messages to regenerate.")
        
    # 2. If it's an assistant message, delete it
    if last_msg.role == "assistant":
        db.delete(last_msg)
        db.commit()
        
    # 3. Get history (which now doesn't include the deleted message, but includes the last user message)
    history = db.query(models.Message).filter(models.Message.session_id == session_id).order_by(models.Message.created_at.asc()).all()
    if not history or history[-1].role != "user":
        # If there's no user message to respond to, we can't regenerate properly
        raise HTTPException(status_code=400, detail="Can only regenerate after a user message.")
        
    history_dicts = [{"role": m.role, "content": m.content} for m in history]

    try:
        assistant_reply = llm.generate_chat_response(history_dicts)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    ast_msg = models.Message(session_id=session_id, role="assistant", content=assistant_reply)
    db.add(ast_msg)
    
    # Update session modified time
    session = db.query(models.Session).filter(models.Session.id == session_id).first()
    if session:
        session.updated_at = ast_msg.created_at
    
    db.commit()

    return {"assistant_message": ast_msg}

@app.post("/api/sessions/{session_id}/upload")
def upload_file(session_id: str, file: UploadFile = File(...), file_type: str = Form(...), db: Session = Depends(get_db)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    doc = models.Document(session_id=session_id, file_name=file.filename, file_type=file_type, file_url=file_path)
    db.add(doc)
    
    sys_msg = models.Message(session_id=session_id, role="system", content=f"User uploaded a {file_type} document: {file.filename}")
    db.add(sys_msg)
    db.commit()
    
    return {"filename": file.filename, "status": "uploaded"}

# Mount frontend
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
