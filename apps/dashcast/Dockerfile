# Código fuente: copia fijada en ./src (TECHO5 commit 4a0760732a572ddca1c2ffcb772c3a17cf03bd9a, dashcast/, MIT)
FROM --platform=$BUILDPLATFORM golang:1.26 AS build
ARG TARGETOS TARGETARCH
WORKDIR /src
COPY src/go.mod src/go.sum ./
RUN go mod download
COPY src/*.go ./
RUN CGO_ENABLED=0 GOOS=$TARGETOS GOARCH=$TARGETARCH go build -trimpath -ldflags="-s -w" -o /dashcast .

FROM chromedp/headless-shell:stable
RUN apt-get update \
 && apt-get install -y --no-install-recommends fonts-noto-core fonts-noto-color-emoji ca-certificates jq util-linux \
 && rm -rf /var/lib/apt/lists/*
COPY --from=build /dashcast /usr/local/bin/dashcast
COPY src/LICENSE /usr/share/doc/dashcast/LICENSE
COPY run.sh /run.sh
RUN chmod +x /run.sh
ENV HOME=/tmp
EXPOSE 9555
ENTRYPOINT ["/run.sh"]
