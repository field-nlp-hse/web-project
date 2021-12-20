# заранее записал 2-3 необходимые команды, позже вольём в основной докерфайл
# исхожу из того, что образ будет Debian, как у всех нормальных людей
RUN apt update
RUN apt install npm
RUN npm install bootstrap@4.6 jquery
RUN wget https://bootswatch.com/4/lux/bootstrap.css -P /node_modules/bootstrap/dist/css/
