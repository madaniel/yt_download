FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py ./

# Create downloads dir
RUN mkdir /downloads

EXPOSE 5000

CMD ["python", "app.py"]
