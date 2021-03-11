FROM python:3.7

WORKDIR /usr/src/app

COPY acknow_mod.py .

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN python -m spacy download en_core_web_sm

VOLUME ["/data/articles"]

VOLUME ["/data/output"]

CMD ["python", "./acknow_mod.py","/data/output"]