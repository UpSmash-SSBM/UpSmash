FROM nikolaik/python-nodejs

WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt

RUN npm install @slippi/slippi-js
RUN python pull_top_50.py

EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "upsmash:create_full_app()"]
