#!/bin/bash

# Script de démarrage de l'application

echo "🚀 Démarrage de l'application Administration des Rapports Réglementaires..."

# Vérifier si le venv existe
if [ ! -d "venv" ]; then
    echo "❌ Environnement virtuel non trouvé. Créez-le d'abord avec : python -m venv venv"
    exit 1
fi

# Activer l'environnement virtuel
source venv/bin/activate

# Vérifier si les dépendances sont installées
echo "📦 Vérification des dépendances..."
pip install -q -r requirements.txt

# Démarrer le serveur
echo "✅ Démarrage du serveur FastAPI sur http://localhost:8000"
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
