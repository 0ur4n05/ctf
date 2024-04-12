FROM ubuntu:22.04
RUN mkdir /app
RUN apt update -y && apt install -y socat build-essential
COPY chall /app/
# COPY flag.txt /app/flag.txt
WORKDIR /app
RUN echo "#!/bin/sh\n/lib64/ld-linux-x86-64.so.2 /app/chall" >> /app/entrypoint.sh && chmod +x /app/entrypoint.sh
# RUN gcc -o chall chall.c
CMD ["sh", "-c", "socat -d TCP-LISTEN:5000,reuseaddr,fork EXEC:/app/entrypoint.sh"]
