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
CMD ["curl -sS https://apertium.projectjj.com/apt/install-nightly.sh | sudo bash"]
RUN apt install hfst -y

WORKDIR /home/app/
COPY . .

RUN pip3 install -r requirements.txt

RUN chmod +x /home/app/run_system.sh
CMD ["/home/app/run_system.sh"]

EXPOSE 80

