FROM python:3.12-slim

# Python sem buffers (logs aparecem em tempo real no dashboard).
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Dependências primeiro: as camadas não mudam quando o código muda.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

# Usuário sem privilégios de root dentro do container.
RUN useradd --create-home appuser && chown -R appuser:appuser /app
USER appuser

# Aplicação escuta em 0.0.0.0 (exigência do ambiente de containers).
EXPOSE 8000

# Verificação de vida para a plataforma (usa só a biblioteca padrão).
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request,sys; r=urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=5); sys.exit(0 if r.status==200 else 1)"

WORKDIR /app/src

# Servidor WSGI de produção (não o de desenvolvimento do Flask).
CMD ["gunicorn", "--workers", "2", "--bind", "0.0.0.0:8000", "--timeout", "120", "webapp:app"]
