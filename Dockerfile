FROM python:3

# should be edited along with the config.py
EXPOSE 8080
WORKDIR /usr/src/app

RUN apt update && apt install -y \
	libmpv-dev \
	alsa-utils \
	libpulse0 \
	xdg-utils
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "run.py" ]

