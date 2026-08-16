from Test.test_main import client
from main import app
from fastapi import status
from User_Authentication.user import decode_token
from Database_connection import sessionlocal
from model import TransactionTable
from datetime import date

def override_decode_token():
    return{
        'id': 1,
        'username': 'testuser'
    }
app.dependency_overrides[decode_token]  = override_decode_token

def test_alltransactions():
    response = client.get('/')
    assert response.status_code == status.HTTP_200_OK


def test_transaction_table():
    db = sessionlocal()

    #remove------
    db.query(TransactionTable).filter(TransactionTable.id == 999).delete()

    transaction = TransactionTable(
            id = 999,
            title = 'Testing',
            amount = 435,
            type = 'Testing',
            category = 'Testing',
            date = date(2026, 8, 16),
            owner_id = 1
    )

    db.add(transaction)
    db.commit()
    

def test_Transaction_ID():
    response = client.get('/transactions/999')
    assert response.status_code == status.HTTP_200_OK


def test_Transaction():

    request_data = {
        "title": "PYTEST_TRANSACTION",
        "amount": 0,
        "type": "string",
        "category": "string",
        "date": "2026-08-16"
        }
    response = client.post('/transactions', json=request_data)
    assert response.status_code == status.HTTP_201_CREATED

    db = sessionlocal()
    db.query(TransactionTable).filter(TransactionTable.title == "PYTEST_TRANSACTION").delete()
    db.commit()
    db.close()


def test_Transaction_Update():

    request_data = {
        "title": "update",
        "amount": 150
        }
    response = client.put('/transactions/999', json=request_data)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == 'Transaction Info Update Sucessfully.'



def test_Delete_Transaction_ID():

    db = sessionlocal()
    
    #remove------
    db.query(TransactionTable).filter(TransactionTable.id == 999).delete()
    db.commit()

    transaction = TransactionTable(
                id = 999,
                title = 'Testing',
                amount = 435,
                type = 'Testing',
                category = 'Testing',
                date = date(2026, 8, 16),
                owner_id = 1
        )
    db.add(transaction)
    db.commit()
    db.close()
    
    response = client.delete('/transactions/999')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == 'Transaction Data Delete Successful.'
