from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from database import *
from models import *
from typing import List

app = FastAPI()

# CREATE USER

@app.post('/users', response_model=userRead)
async def create_user(newUser: user, db: Session = Depends(get_db)):
    
    exists = db.query(UserDB).filter(UserDB.username == newUser.username).first()
    
    if exists:
        raise HTTPException(status_code=409, detail="username is already being used")
    
    db_user = UserDB(**newUser.model_dump())
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user

# GET ALL USERS

@app.get('/users', response_model=List[userRead])
async def get_all_users(db: Session = Depends(get_db)):
    
    users = db.query(UserDB).all()
    
    return users
    
# FIND USER BY ID
    
@app.get('/users/{id}', response_model=userRead)
async def find_user_by_id(id: int, db:Session = Depends(get_db)):
    
    db_user = db.query(UserDB).filter(UserDB.id == id).first()
    
    if db_user is None:
        raise HTTPException(status_code=404, detail='User Not Found')

    return db_user

# DELETE USER

@app.delete('/users/{id}')
async def delete_user(id : int, db: Session = Depends(get_db)):
    
    db_user = db.query(UserDB).filter(UserDB.id == id).first()
    
    if db_user:
        db.delete(db_user)
        db.commit()
        
        return {
            'message': f'User with id "{id}" was deleted',
            'Deleted User': db_user
            }
    
    else:
        raise HTTPException(status_code=404, detail='User Not Found')
    

if __name__ == '__main__':
    import uvicorn
    uvicorn.run("main:app", host = '0.0.0.0', port=8000, reload=True)
