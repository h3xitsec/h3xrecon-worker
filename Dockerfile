ARG SERVER_VERSION="dev"

FROM ghcr.io/h3xitsec/h3xrecon_server:${SERVER_VERSION}

ENV PATH="$PATH:/root/go/bin:/root/.pdtm/go/bin:/usr/lib/go-1.15/bin"

RUN apt-get update && apt-get install -y \
    golang-go \
    jq \
    prips \
    nmap \
    && rm -rf /var/lib/apt/lists/*

RUN go install -v github.com/projectdiscovery/pdtm/cmd/pdtm@latest && \
    pdtm -i subfinder && \
    pdtm -i httpx && \
    pdtm -i dnsx

RUN git clone https://github.com/UnaPibaGeek/ctfr.git /opt/ctfr && \
    cd /opt/ctfr && \
    pip install -r requirements.txt

RUN go install github.com/Josue87/gotator@latest

RUN python3 -m venv /app/venv && \
    /app/venv/bin/pip install --upgrade pip && \
    /app/venv/bin/pip install --no-cache-dir git+https://github.com/h3xitsec/h3xrecon-worker@v0.0.3

ENTRYPOINT ["/app/venv/bin/h3xrecon-worker"]