
#Deriving the latest base image
FROM python:latest
#Labels as key value pair
LABEL Maintainer="cp.scraper"

# Any working directory can be chosen as per choice like '/' or '/home' etc
# i have chosen /usr/app/src
WORKDIR /usr/app/src

#to COPY the remote file at working directory in container

COPY app.py ./
COPY scrapeCP.py ./
COPY utils.py ./
COPY scraper.db ./
# Now the structure looks like this '/usr/app/src/test.py'
ADD templates ./templates
ADD static ./static
ADD data ./data

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

#CMD instruction should be used to run the software
#contained by your image, along with any arguments.

CMD [ "python", "./app.py"]
