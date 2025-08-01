from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from uuid import UUID, uuid4
from datetime import date, time
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


class TransactionIn(BaseModel):
    date: date
    heure: time
    montant: float
    type_transaction: str
    numero_destinataire: str

class Transaction(TransactionIn):
    id: UUID

transactions: List[Transaction] = []

# Route d'accueil pour charger index.html
@app.get("/")
def lire_page():
    return FileResponse("static/index.html")

@app.post("/transactions", response_model=Transaction)
def ajouter_transaction(data: TransactionIn):
    d = data.dict()
    d["type_transaction"] = d["type_transaction"].lower()
    if d["type_transaction"] not in ["depot", "retrait"]:
        raise HTTPException(status_code=400, detail="Type de transaction invalide.")
    t = Transaction(id=uuid4(), **d)
    transactions.append(t)
    return t


@app.get("/transactions", response_model=List[Transaction])
def lire_transactions():
    return transactions

@app.get("/transactions/{transaction_id}", response_model=Transaction)
def lire_transaction(transaction_id: UUID):
    for t in transactions:
        if t.id == transaction_id:
            return t
    raise HTTPException(status_code=404, detail="Transaction non trouvée")

@app.put("/transactions/{transaction_id}", response_model=Transaction)
def modifier_transaction(transaction_id: UUID, data: TransactionIn):
    d = data.dict()
    d["type_transaction"] = d["type_transaction"].lower()
    if d["type_transaction"] not in ["depot", "retrait"]:
        raise HTTPException(status_code=400, detail="Type de transaction invalide.")
    for index, t in enumerate(transactions):
        if t.id == transaction_id:
            updated = Transaction(id=transaction_id, **d)
            transactions[index] = updated
            return updated
    raise HTTPException(status_code=404, detail="Transaction non trouvée")

@app.delete("/transactions/{transaction_id}")
def supprimer_transaction(transaction_id: UUID):
    for index, t in enumerate(transactions):
        if t.id == transaction_id:
            transactions.pop(index)
            return {"message": "Transaction supprimée"}
    raise HTTPException(status_code=404, detail="Transaction non trouvée")
