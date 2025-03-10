from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from database import *
from models import *
from typing import List
from methods import create_access_token
import requests 

app = FastAPI()

# GET ALL USERS

@app.get('/users', response_model=List[userRead], tags=['users'])
async def get_all_users(db: Session = Depends(get_db)):
    
    users = db.query(UserDB).all()
        
    if len(users) <= 0:
        raise HTTPException(status_code=404, detail="User not found!")

    
    return users
    
# FIND USER BY ID

@app.get('/users/{id}', response_model=userRead, tags=['users'])
async def find_user_by_id(id: int, db:Session = Depends(get_db)):
    
    db_user = db.query(UserDB).filter(UserDB.id == id).first()
    
    if db_user is None:
        raise HTTPException(status_code=404, detail='User Not Found')

    return db_user

# CREATE USER

@app.post('/users', response_model=userRead, tags=['users'])
async def create_user(newUser: user, db: Session = Depends(get_db)):
    
    exists = db.query(UserDB).filter(UserDB.username == newUser.username).first()
    
    if exists:
        raise HTTPException(status_code=409, detail="username is already being used")
    
    # TOKEN GEN FUNCTION
    
    newUser.token = create_access_token(newUser.username)
    
    db_user = UserDB(**newUser.model_dump())
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user

# DELETE USER

@app.delete('/users/{id}', tags=['users'])
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

# UPDATE USER

@app.put('/users/{id}', response_model=userRead, tags=['users'])
async def update_user(id: int, upd_user: user , db: Session = Depends(get_db)):
    
    db_user = db.query(UserDB).filter(UserDB.id == id).first()
    
    if not db_user:
        raise HTTPException(status_code=404, detail='User Not Found')
    
    for key, value in upd_user.dict().items():
        setattr(db_user, key, value)
            
    db_user.token = create_access_token(upd_user.username)
        
    db.commit()
    db.refresh(db_user)
    
    return db_user

@app.get('/tokens', tags=['tokens'])
async def get_tokens(db: Session = Depends(get_db)):
    lista = []
    
    tokens = db.query(UserDB).all()
    
    if len(tokens) <= 0:
        raise HTTPException(status_code=404, detail="Token not found!")
    
    for i in tokens:
        lista.append(i.token)

    return lista

# API AMBER PEGANDO TOKEN

@app.get('/token_gen/{username}', tags=['tokens'])
async def get_token_by_username(username: str):
    
    token = create_access_token(username=username)
    
    return token


@app.get('/api/matches',  tags=['matches'])
async def get_matches():
    
    lista = []
    
    response = requests.get('https://api.sportmonks.com/v3/football/fixtures/upcoming/markets/1?api_token=5kmSGVTWIc73kw3gSY9txBnQS1QoR2UfyZ3OEcuKPGQVE3qpMuO9bZZVQFDb')
    data = response.json()
    
    if 'message' in data:
        if data['message'] == "No result(s) found matching your request. Either the query did not return any results or you don't have access to it via your current subscription.":
            raise HTTPException(status_code=404, detail="Match Not Found")
    
    for match in data['data']:
        if match['has_odds'] == True:
                        
            objeto = {}
                        
            id = match['id']
            name = match['name']
            date = match['starting_at']
            
            # Consumindo API da amber que possui as ODDS
            
            # IP AMBER REDE BTC 5
            #   192.168.88.122
            
            #IP BOSCH
            # 10.234.93.94
            
            response = requests.get(f'http://10.234.93.94:8000/api/match/{id}')
            data = response.json()
            
            objeto['id'] = id
            objeto['name'] = name
            objeto['date'] = date
            objeto['odd'] = data
            
        lista.append(objeto)
            
    return lista

# GET MATCH BY ID

@app.get('/api/matches/{id}',  tags=['matches'])
async def get_match_by_id(id: int):
    
    # TRATAR EXCEÇÔES
    
    response = requests.get(f"https://api.sportmonks.com/v3/football/fixtures/{id}?api_token=5kmSGVTWIc73kw3gSY9txBnQS1QoR2UfyZ3OEcuKPGQVE3qpMuO9bZZVQFDb")
    data = response.json()
    
    if 'message' in data:
        if data['message'] == "No result(s) found matching your request. Either the query did not return any results or you don't have access to it via your current subscription.":
            raise HTTPException(status_code=404, detail="Match Not Found")

    match = data['data']
        
    objeto = {}
    
    id = match['id']
    name = match['name']
    date = match['starting_at']
    
    objeto['id'] = id
    objeto['name'] = name
    objeto['date'] = date
    
    return objeto


if __name__ == '__main__':
    import uvicorn
    uvicorn.run("main:app", host='0.0.0.0', port=8000, reload=True)
