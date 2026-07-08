# Superset Deploy Runbook

Servidor alvo: DockerServer (192.168.15.76)

## Objetivo

Atualizar o codigo, reconstruir a imagem do Superset e recriar o container em producao.

## 1) Acessar o servidor

	ssh <usuario>@192.168.15.76

## 2) Ir para o diretorio do projeto

	cd superset

## 3) Limpeza de imagens/cache Docker

	docker system prune -af

## 4) Atualizar codigo

	git pull

## 5) Build da imagem de producao

	sudo docker compose -f docker-compose-prod.yml --env-file docker/.env-prod build --no-cache --pull superset

## 6) Derrubar stack atual

	sudo docker compose -f docker-compose-prod.yml --env-file docker/.env-prod down

## 7) Subir stack com container recriado

	sudo docker compose -f docker-compose-prod.yml --env-file docker/.env-prod up -d --force-recreate superset

## 8) Verificacao rapida

	sudo docker compose -f docker-compose-prod.yml --env-file docker/.env-prod ps
	sudo docker compose -f docker-compose-prod.yml --env-file docker/.env-prod logs --tail=200 superset
