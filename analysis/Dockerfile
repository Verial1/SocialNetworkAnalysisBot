FROM python:3.12-slim

ENV CUDA_VISIBLE_DEVICES=0

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "analysis_batch.py"]