FROM kalilinux/kali-rolling:amd64
LABEL authors="ronan"


CMD apt-get update
CMD apt-get install -y cargo
CMD cargo install -y rustscan

CMD apt-get install -y python3 python3-pip

WORKDIR /hunter

COPY requirements.txt .

CMD pip3 install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT ["python3", "main.py"]
