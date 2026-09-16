
FROM alpine:latest

RUN apk add python3 py3-pip openssh wget bash git && \
	adduser -D cmu-bsit

WORKDIR /home/cmu-bsit

COPY . .

RUN git config --global --add safe.directory /home/cmu-bsit && \
	echo $(git rev-parse --short HEAD) > ./version

RUN pip3 install -r requirements.txt --break-system-packages
USER cmu-bsit
#EXPOSE 8000
CMD ["python3", "main.py"]
