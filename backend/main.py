from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import pandas as pd
from sqlalchemy import text
import dwh_connect

app = FastAPI(title="Regulatory Reports Administration")

# Configuration CORS pour permettre les requêtes depuis le frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir les fichiers statiques
app.mount("/static", StaticFiles(directory="../frontend/static"), name="static")


# Modèles Pydantic
class Fund(BaseModel):
    Mnemo_Fund: str
    Lib_Fund: str


class EETField(BaseModel):
    version: str
    field_name: str
    is_fixed_value: Optional[str] = None
    value_source: Optional[str] = None
    is_filed_in: Optional[str] = None
    requirement_type: Optional[str] = None
    format: Optional[str] = None
    remarques: Optional[str] = None


class ValidationRequest(BaseModel):
    request_type: str  # 'INSERT', 'UPDATE', 'DELETE'
    table_name: str
    data: Dict[str, Any]
    status: str = 'PENDING'  # 'PENDING', 'APPROVED', 'REJECTED'


# Routes de base
@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Page d'accueil"""
    with open("../frontend/templates/index.html", "r", encoding="utf-8") as f:
        return f.read()


@app.get("/api/funds", response_model=List[Fund])
async def get_funds():
    """Récupère la liste de tous les fonds"""
    try:
        engine = dwh_connect.connect_engine()
        query = "SELECT Mnemo_Fund, Lib_Fund FROM Ref_Funds"
        df = dwh_connect.read_sql_dataframe(query, engine)
        return df.to_dict('records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des fonds: {str(e)}")


@app.get("/api/eet-fields", response_model=List[EETField])
async def get_eet_fields(version: Optional[str] = None):
    """Récupère les templates de reporting (tb_eet_fields)"""
    try:
        engine = dwh_connect.connect_engine()
        query = """
            SELECT version, field_name, is_fixed_value, value_source,
                   is_filed_in, requirement_type, format, remarques
            FROM tb_eet_fields
        """
        if version:
            query += f" WHERE version = '{version}'"

        df = dwh_connect.read_sql_dataframe(query, engine)
        return df.to_dict('records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des champs EET: {str(e)}")


@app.get("/api/eet-versions")
async def get_eet_versions():
    """Récupère la liste des versions disponibles dans tb_eet_fields"""
    try:
        engine = dwh_connect.connect_engine()
        query = "SELECT DISTINCT version FROM tb_eet_fields ORDER BY version"
        df = dwh_connect.read_sql_dataframe(query, engine)
        return {"versions": df['version'].tolist()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des versions: {str(e)}")


@app.post("/api/validation-requests")
async def create_validation_request(request: ValidationRequest):
    """Crée une demande de validation pour INSERT/UPDATE/DELETE"""
    try:
        engine = dwh_connect.connect_engine()
        connection = engine.connect()

        # Insérer dans tb_validation_requests
        insert_data = {
            'request_type': request.request_type,
            'table_name': request.table_name,
            'data': str(request.data),
            'status': request.status
        }

        dwh_connect.insert_into_table(connection, 'tb_validation_requests', insert_data)

        return {
            "message": "Demande de validation créée avec succès",
            "request": request.dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création de la demande: {str(e)}")


@app.get("/api/validation-requests")
async def get_validation_requests(status: Optional[str] = None):
    """Récupère les demandes de validation"""
    try:
        engine = dwh_connect.connect_engine()
        query = "SELECT * FROM tb_validation_requests"
        if status:
            query += f" WHERE status = '{status}'"
        query += " ORDER BY created_at DESC"

        df = dwh_connect.read_sql_dataframe(query, engine)
        return df.to_dict('records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des demandes: {str(e)}")


@app.get("/health")
async def health_check():
    """Vérification de l'état de l'application"""
    try:
        engine = dwh_connect.connect_engine()
        connection = engine.connect()
        result = dwh_connect.test_connection(connection)
        return {
            "status": "healthy",
            "database": result
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
