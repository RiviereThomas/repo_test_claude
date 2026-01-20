@echo off
REM Script de démarrage de l'application (Windows)

echo 🚀 Démarrage de l'application Administration des Rapports Réglementaires...

REM Vérifier la version de Python
echo 📌 Utilisation de Python :
python --version

REM Vérifier et installer les dépendances
echo 📦 Vérification des dépendances...
pip install -q -r requirements.txt

REM Démarrer le serveur
echo ✅ Démarrage du serveur FastAPI sur http://localhost:8000
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
