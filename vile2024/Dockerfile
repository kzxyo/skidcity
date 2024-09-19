FROM python:3.11.1

RUN apt update -y && apt install fonts-liberation libatk-bridge2.0-0 libatk1.0-0 libatspi2.0-0 libcups2 libgtk-3-0 libu2f-udev libxcomposite1 xdg-utils cargo lshw nano openssh-server tesseract-ocr mariadb-server redis-server build-essential software-properties-common sudo wget curl nmap neofetch telnet iputils-* iproute2 facter git ufw zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev ffmpeg libbz2-dev libsqlite3-dev llvm libncursesw5-dev xz-utils tk-dev liblzma-dev python3-openssl fail2ban -y
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && dpkg -i google-chrome-stable_current_amd64.deb && apt install -f

WORKDIR /app
ENTRYPOINT ["python", "main.py"]
