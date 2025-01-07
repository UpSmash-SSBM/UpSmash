FROM nikolaik/python-nodejs

WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt

RUN npm install @slippi/slippi-js
RUN python pull_top_50.py

EXPOSE 5000
ENTRYPOINT ["python"]
CMD ["run.py"]