FROM kalilinux/kali-rolling:amd64
LABEL authors="ronan"


RUN apt-get update
RUN apt-get install -y cargo
RUN cargo install rustscan

RUN apt-get install -y python3 python3-pip

WORKDIR /hunter

COPY requirements.txt .

RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

COPY . .

ENTRYPOINT ["python3", "main.py"]
