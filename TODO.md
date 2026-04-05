# Rezervasyon TS Error Fix - TODO
docker-compose up -d

docker-compose down

pip install -r requirements.txt

python -m app.init_db

uvicorn app.main:app --reload

npm run dev
