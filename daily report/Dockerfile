FROM public.ecr.aws/lambda/python:3.12

COPY report_requirements.txt .

RUN pip install -r report_requirements.txt

COPY generate_report.py .

CMD ["generate_report.lambda_handler"]
