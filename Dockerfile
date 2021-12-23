FROM ubuntu:20.04

LABEL maintainer="alexanderbaranof@gmail.com"

ENV TZ=Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN apt update
RUN apt install -y git
RUN apt install -y python3
RUN apt install -y python3-pip
RUN apt install -y curl
RUN apt install -y wget
RUN /bin/bash -c "curl -sS https://apertium.projectjj.com/apt/install-nightly.sh | bash"
RUN apt install hfst -y
RUN apt install -y nodejs
RUN apt install -y npm

WORKDIR /home/app/
COPY . .

RUN pip3 install -r requirements.txt
RUN npm install .
RUN /bin/bash -c "wget -P /home/app/static/css/ https://bootswatch.com/4/lux/bootstrap.css"

RUN chmod +x /home/app/run_system.sh
CMD ["/home/app/run_system.sh"]

EXPOSE 80

