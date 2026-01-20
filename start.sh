#!/bin/bash

# Script de démarrage de l'application

echo "🚀 Démarrage de l'application Administration des Rapports Réglementaires..."

# Vérifier la version de Python
echo "📌 Utilisation de Python : $(python3 --version)"

# Vérifier si les dépendances sont installées
echo "📦 Vérification des dépendances..."
pip3 install -q -r requirements.txt

# Démarrer le serveur
echo "✅ Démarrage du serveur FastAPI sur http://localhost:8000"
cd backend
python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
