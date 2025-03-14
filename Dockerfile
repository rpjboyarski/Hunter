FROM kalilinux/kali-rolling:amd64
LABEL authors="ronan"

ENTRYPOINT ["top", "-b"]

CMD apt-get update
CMD apt-get install -y cargo
CMD cargo install -y rustscan