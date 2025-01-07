FROM nikolaik/python-nodejs

WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt

RUN npm install @slippi/slippi-js

EXPOSE 5000
ENTRYPOINT ["python"]
CMD ["run.py"]