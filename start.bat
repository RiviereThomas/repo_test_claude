@echo off
REM Script de démarrage de l'application (Windows)

echo 🚀 Démarrage de l'application Administration des Rapports Réglementaires...

REM Vérifier si le venv existe
if not exist "venv\" (
    echo ❌ Environnement virtuel non trouvé. Créez-le d'abord avec : python -m venv venv
    exit /b 1
)

REM Activer l'environnement virtuel
call venv\Scripts\activate.bat

REM Vérifier et installer les dépendances
echo 📦 Vérification des dépendances...
pip install -q -r requirements.txt

REM Démarrer le serveur
echo ✅ Démarrage du serveur FastAPI sur http://localhost:8000
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
