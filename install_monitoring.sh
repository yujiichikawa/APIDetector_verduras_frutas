#!/bin/bash

# Script de instalação do Docker e Docker Compose no Ubuntu 24.04 LTS
# Desenvolvido para fins educacionais - Evandro José Zipf

# Encerra a execução se ocorrer qualquer erro em um comando
set -e

echo "[1/7] Atualizando o índice de pacotes..."
# Atualiza apenas a lista de pacotes disponíveis (não instala nem atualiza nenhum pacote do sistema)
sudo apt update

echo "[2/7] Instalando dependências necessárias..."
# Instala ferramentas essenciais:
# - ca-certificates: garante que conexões HTTPS sejam validadas com certificados
# - curl: ferramenta para baixar arquivos via HTTP/HTTPS
# - gnupg: utilitário de criptografia usado para importar a chave GPG
# - lsb-release: usado para detectar a versão do Ubuntu (ex: 24.04)
sudo apt install -y ca-certificates curl gnupg lsb-release

echo "[3/7] Adicionando a chave GPG oficial do Docker..."
# Cria o diretório onde as chaves APT modernas devem ser armazenadas (se ainda não existir)
sudo install -m 0755 -d /etc/apt/keyrings

# Baixa a chave GPG do repositório oficial do Docker e converte para o formato usado pelo APT
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
  sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Ajusta permissões para que o APT consiga ler a chave
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo "[4/7] Adicionando o repositório oficial do Docker à lista de fontes APT..."
# Adiciona o repositório do Docker, indicando:
# - arquitetura da máquina
# - que a chave GPG está localizada em /etc/apt/keyrings/docker.gpg
# - a versão do Ubuntu será automaticamente detectada com $(lsb_release -cs)
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

echo "[5/7] Atualizando o índice de pacotes novamente..."
# Atualiza a lista de pacotes para incluir os pacotes do novo repositório (Docker)
sudo apt update

echo "[6/7] Instalando o Docker e o plugin Docker Compose..."
# Instala os principais componentes:
# - docker-ce: Engine do Docker
# - docker-ce-cli: Ferramenta de linha de comando do Docker
# - containerd.io: Runtime container usado pelo Docker
# - docker-buildx-plugin: Plugin de build avançado (buildx)
# - docker-compose-plugin: Versão atual do Docker Compose integrada ao Docker CLI
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

echo "[7/7] Verificando se tudo foi instalado corretamente..."
# Verifica se o Docker e o Compose responderam corretamente
docker --version
docker compose version

echo "✅ Docker e Docker Compose instalados com sucesso!"
echo "ℹ️ Caso deseje executar Docker sem 'sudo', adicione seu usuário ao grupo 'docker':"
echo "   sudo usermod -aG docker \$USER && newgrp docker"

# Caminho do arquivo de composição
COMPOSE_FILE="docker-compose.yml"

# Verifica se o arquivo existe antes de rodar
if [ -f "$COMPOSE_FILE" ]; then
    echo "📂 Encontrado: $COMPOSE_FILE"
    echo "🚀 Iniciando os containers com Docker Compose..."
    docker compose -f "$COMPOSE_FILE" up -d
    echo "✅ Containers iniciados com sucesso!"
else
    echo "⚠️ Arquivo $COMPOSE_FILE não encontrado. Nenhum container foi iniciado."
    echo "💡 Verifique o caminho e certifique-se de que o arquivo existe."
fi