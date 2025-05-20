# Projet-MOOC

Projet Data IA 2024 - Greta Centre Val de Loire/Simplonline - MOOC

## Creation de l'environnement virtuel sous Linux
```bash
    # Création environnement virtuel & activation
    python3 -m venv venv
    source venv/bin/activate
    # Installation librairies listées dans 'requirements.txt'
    pip install -r requirements.txt
    pip freeze
```
## Creation de l'environnement Virtuel sous windows
```shell
  # Création de l'environnement virtuel
  python -m venv venv
  # Activation de l'environnement virtuel
  .\venv\Scripts\activate
  # Installation des librairies listées dans 'requirements.txt'
  pip install -r requirements.txt
  # Affichage des librairies installées dans l'environnement virtuel
  pip freeze
```

## Déactivation de l'environnement virtuel
```
 deactivate 
```

## lancer l'application :
```python
#Ouvre un terminal dans le dossier app/, puis lance :
uvicorn main:app --reload
```


## Docker

```bash
    # Afficher tous les conteneurs (y compris ceux arrêtés)
    docker ps -a
    docker start <nom_du_conteneur>
    # Verifier les contenenurs lancés
    docker ps
```