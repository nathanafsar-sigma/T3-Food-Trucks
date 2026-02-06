FROM python:3.12

WORKDIR /app

COPY pipeline_requirements.txt .

RUN pip install -r pipeline_requirements.txt

COPY extract.py transform.py create_parquet.py upload_to_s3.py pipeline.py ./

RUN mkdir -p data/raw data/clean data/parquet data/outputs

CMD ["python", "pipeline.py"]
