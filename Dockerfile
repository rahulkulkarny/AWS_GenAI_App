
# docker build --platform linux/x86_64 -t AWS_GenAI_App .
FROM python:3.11-slim

WORKDIR /app


COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app.py agent.py SaraswatiMaa.avif .

# docker run --platform linux/x86_64 -p 8080:8080 --env-file .env AWS_GenAI_App
CMD ["python", "app.py"]
