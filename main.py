from fastapi import FastAPI, Depends, HTTPException
from Database_connection import sessionlocal
from fastapi.responses import JSONResponse
from Database_connection import engine
from typing import Annotated, Optional
from User_Authentication import user
from model import TransactionTable
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from User_Authentication.user import decode_token
from datetime import date
import model

app = FastAPI()

model.Base.metadata.create_all(bind=engine)
app.include_router(user.router)

def database_open():
    db = sessionlocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(database_open)]
user_dependency = Annotated[dict, Depends(decode_token)]

@app.get('/')
def alltransactions(db:db_dependency):
    return db.query(TransactionTable).all()

#---------------------specific transaction----------------------#
@app.get('/transactions/{transaction_id}')
def Transaction_ID(db: db_dependency, user: user_dependency, transaction_id: int):
    search_transaction = db.query(TransactionTable).filter(TransactionTable.id == transaction_id).filter(TransactionTable.owner_id == user.get('id')).first()

    if user is None:
        return JSONResponse(status_code=401, content='You must be logged in to perform this action.')
    if search_transaction is None:
        return JSONResponse(status_code=404, content='Not Found ID')
    else:
        return search_transaction

    
#----------------------Create Transaction-----------------------#
class TransactionCreate(BaseModel):
    title: str
    amount: float
    type: str
    category: str
    date: date

@app.post('/transactions')
def Transaction(db:db_dependency, user: user_dependency, new_transaction: TransactionCreate):
    if user is None:
        return JSONResponse(status_code=401, content='You must be logged in to perform this action.')
    new_transaction_upload = TransactionTable(**new_transaction.model_dump(), owner_id = user.get('id'))
    db.add(new_transaction_upload)
    db.commit()
    return JSONResponse(status_code=201, content="Transaction created successfully")

#----------------------Transaction Update-----------------------#
class TransactionUpdate(BaseModel):
    title: Optional[str] = None
    amount: Optional[float] = None
    type: Optional[str] = None
    category: Optional[str] = None
    date: Optional[date] = None

@app.put('/transactions/{transaction_id}')
def Transaction_Update(db: db_dependency, user: user_dependency, transaction_update: TransactionUpdate, transaction_id: int):
    update_transaction = db.query(TransactionTable).filter(TransactionTable.id == transaction_id).filter(TransactionTable.owner_id == user.get('id')).first()

    if user is None:
        return JSONResponse(status_code=401, content='You must be logged in to perform this action.')
    
    if update_transaction is None:
        return JSONResponse(status_code=404, content='Not Found ID')

    update_transaction_value = transaction_update.model_dump(exclude_unset=True)
    for key, value in update_transaction_value.items():
        setattr(update_transaction, key, value)
    db.commit()
    return JSONResponse(status_code=200, content='Transaction Info Update Sucessfully.')


#----------------------Transaction Delete-----------------------#
@app.delete('/transactions/{transaction_id}')
def Transaction_ID(db: db_dependency, user: user_dependency, transaction_id: int):
         
        if user is None:
            return JSONResponse(status_code=401, content='You must be logged in to perform this action.')
         
        Delete_Transaction = db.query(TransactionTable).filter(TransactionTable.id == transaction_id).filter(TransactionTable.owner_id == user.get('id')).first()
            
        if Delete_Transaction is None:
            return JSONResponse(status_code=404, content='Transaction ID Not Found')

        db.delete(Delete_Transaction)
        db.commit()
        return JSONResponse(status_code=200, content='Transaction Data Delete Successful.')

#-------------------Transaction-filter-------------------------#

@app.get('/transaction/filter')
def Transaction_Filter(
    db: db_dependency, 
    user: user_dependency, 
    type: Optional[str] = None,
    category: Optional[str] = None,
    minimum_amount: Optional[float] = None,
    maximum_amount: Optional[float] = None
    ):

    if user is None:
        return JSONResponse(status_code=401, content='You must be logged in to perform this action.')
     
    query = db.query(TransactionTable).filter(TransactionTable.owner_id == user.get('id'))
    
    if type is not None:
        query = query.filter(type == TransactionTable.type)

    if category is not None:
        query = query.filter(category == TransactionTable.category)

    if maximum_amount is not None:
        query = query.filter(maximum_amount <= TransactionTable.amount)

    if minimum_amount is not None:
        query = query.filter(minimum_amount >= TransactionTable.amount)

    return query.all()