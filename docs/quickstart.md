git clone https://github.com/SemeAIPletinnya/silence-as-control.git
cd silence-as-control
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python run.py
Invoke-RestMethod -Uri "http://localhost:8000/decide" -Method POST -Body '{"signals":{"coherence":0.5,"drift":0.1,"conflict":0.1,"ambiguity":0.1,"continuity":true}}' -ContentType "application/json"
