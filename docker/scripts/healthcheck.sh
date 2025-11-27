#!/bin/sh
# Healthcheck simples
wget --no-verbose --tries=1 --spider http://localhost:8000/health || exit 1