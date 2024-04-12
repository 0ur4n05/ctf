FROM pwn.red/jail

COPY --from=ubuntu:22.04 / /srv
COPY elf /srv/app/
COPY sysdeps /srv/app/
COPY chal /srv/app/run
COPY lib /srv/app/lib/
COPY flag.txt /srv/app/
