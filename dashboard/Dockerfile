FROM python:3.12

WORKDIR /app

COPY dashboard_requirements.txt .

RUN pip install -r dashboard_requirements.txt

COPY dashboard.py queries.py ./

EXPOSE 8501

CMD ["streamlit", "run", "dashboard.py", "--server.address", "0.0.0.0", "--server.port", "8501"]
