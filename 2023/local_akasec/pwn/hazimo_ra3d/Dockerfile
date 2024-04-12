FROM debian
RUN apt update & apt install socat -y
EXPOSE 1337
COPY hr /home/ctf/
WORKDIR /home/ctf
CMD ["socat", "tcp-l:1337,reuseaddr,fork", "EXEC:./hr"]
