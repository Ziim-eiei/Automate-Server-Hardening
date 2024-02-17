FROM python:3.10

WORKDIR /ash

COPY requirements.txt ./
RUN pip install -r requirements.txt && pip install ansible pywinrm

COPY app .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
