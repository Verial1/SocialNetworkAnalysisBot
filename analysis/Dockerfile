FROM python:3.12-slim

# Fondamentale per usare la GPU NVIDIA dentro Docker
# (Richiede NVIDIA Container Toolkit su WSL2)
ENV CUDA_VISIBLE_DEVICES=0

WORKDIR /app

COPY requirements.txt .
# Attenzione: qui installerai torch, clip, pandas, polars...
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "analysis_batch.py"]