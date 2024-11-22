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

COPY ./h3xrecon-core/src/h3xrecon_core /app/h3xrecon_core
COPY ./h3xrecon-plugins/src/h3xrecon_plugins /app/h3xrecon_plugins
COPY ./h3xrecon-worker/src/h3xrecon_worker /app/h3xrecon_worker
COPY ./h3xrecon-worker/requirements.txt /app/requirements.txt

RUN rm -rf /app/venv && \
    python3 -m venv /app/venv && \
    /app/venv/bin/pip install -r /app/requirements.txt

ENTRYPOINT ["/app/venv/bin/python3", "-m", "h3xrecon_worker.main"]