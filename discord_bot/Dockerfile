FROM python:3.13-slim

WORKDIR /app

# Qui potresti aver bisogno di librerie per l'analisi immagini se la fai nel bot
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Il bot non espone porte, si connette lui a Discord
CMD ["python", "bot.py"]