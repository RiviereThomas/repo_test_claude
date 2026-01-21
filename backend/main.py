from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import pandas as pd
from sqlalchemy import text
import dwh_connect
import eet_calculator

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


@app.get("/eet-fields-viewer", response_class=HTMLResponse)
async def eet_fields_viewer():
    """Page de visualisation complète des champs EET"""
    with open("../frontend/templates/eet_fields.html", "r", encoding="utf-8") as f:
        return f.read()


@app.get("/eet-production", response_class=HTMLResponse)
async def eet_production():
    """Page de production EET"""
    with open("../frontend/templates/eet_production.html", "r", encoding="utf-8") as f:
        return f.read()


@app.get("/api/funds", response_model=List[Fund])
async def get_funds():
    """Récupère la liste de tous les fonds"""
    try:
        engine = dwh_connect.connect_engine()
        query = "SELECT Mnemo_Fund, Lib_Fund FROM Ref_Funds WHERE PTF_Reel = '1'"
        df = dwh_connect.read_sql_dataframe(query, engine)
        # Remplacer les NaN par None
        df = df.where(pd.notna(df), None)
        return df.to_dict('records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des fonds: {str(e)}")


@app.get("/api/funds-details")
async def get_funds_details():
    """Récupère la liste de tous les fonds avec leurs détails (SFDR, Public/Dédié)"""
    try:
        engine = dwh_connect.connect_engine()

        # Essayer avec toutes les colonnes et le filtre PTF_Reel
        query = "SELECT Mnemo_Fund, Lib_Fund, sfdr_cat, Public_Dedie FROM Ref_Funds WHERE PTF_Reel = '1' ORDER BY Mnemo_Fund"
        df = dwh_connect.read_sql_dataframe(query, engine)

        # Remplacer les NaN par None pour la sérialisation JSON
        df = df.where(pd.notna(df), None)

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
    """Récupère la liste des versions disponibles dans tb_eet_fields (triées par ordre décroissant)"""
    try:
        engine = dwh_connect.connect_engine()
        query = "SELECT DISTINCT version FROM tb_eet_fields ORDER BY version DESC"
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


@app.get("/api/fund-results/{fund}")
async def get_fund_results(fund: str, version: Optional[str] = 'EET_1_1_3', date_calcul: Optional[str] = '31/12/2024'):
    """Calcule et retourne les résultats EET pour un fonds donné"""
    try:
        results = eet_calculator.calculate_fund_results(fund, version, date_calcul)
        return {
            "fund": fund,
            "version": version,
            "date_calcul": date_calcul,
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du calcul des résultats: {str(e)}")


class EETGenerationRequest(BaseModel):
    funds: List[str]
    version: str
    date_calcul: str


@app.post("/api/generate-eet")
async def generate_eet(request: EETGenerationRequest):
    """Génère un fichier Excel EET pour plusieurs fonds"""
    try:
        filepath, filename = eet_calculator.generate_eet_excel(
            request.funds,
            request.version,
            request.date_calcul
        )

        return FileResponse(
            path=filepath,
            filename=filename,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la génération du fichier: {str(e)}")


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
