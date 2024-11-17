FROM h3xrecontest/h3xrecon_server:v0.0.1

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

RUN rm -rf /app/venv && \
    python3 -m venv /app/venv && \
    /app/venv/bin/pip install https://github.com/h3xitsec/h3xrecon-worker/releases/download/v0.0.1/h3xrecon_worker-0.0.1-py3-none-any.whl

ENTRYPOINT ["/app/venv/bin/python3", "-m", "h3xrecon_worker.main"]