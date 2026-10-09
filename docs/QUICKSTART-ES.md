# Inicio rápido — prueba Devsu

## 1. Validar en tu PC

Abre Docker Desktop con contenedores Linux. Descomprime el ZIP, entra en la carpeta del proyecto
y abre PowerShell allí. Si tienes Python instalado:

```powershell
py scripts/init-env.py
docker compose up --build -d
docker compose ps
curl.exe http://localhost:8000/health/ready/
py scripts/smoke.py http://localhost:8000
```

El último comando crea y elimina un usuario sintético. No usa datos reales.
Si el puerto 8000 está ocupado, modifica únicamente el puerto izquierdo en `compose.yaml`.
Si no tienes Python, copia `.env.example` a `.env`, reemplaza los dos valores de ejemplo por
valores aleatorios y ejecuta los comandos de Docker. Para consultar logs:

```powershell
docker compose logs --tail 100 api migrate db
```

## 2. Publicar el repositorio

Crea en GitHub un repositorio público vacío, por ejemplo `devsu-devops`, sin README inicial.
En PowerShell, dentro del proyecto:

```powershell
git init
git add .
git status
git commit -m "Implement Devsu DevOps assessment"
git branch -M main
git remote add origin https://github.com/TU-USUARIO/devsu-devops.git
git push -u origin main
```

Comprueba en `git status` que no aparece `.env`, bases de datos, credenciales ni estado de Terraform.
El workflow comenzará al subir `main`. GitHub te pedirá tu autenticación habitual para el push.
No se requieren secretos manuales para el pipeline por defecto.

## 3. Verificar Actions y descargar evidencias

Abre la pestaña **Actions**. Los jobs esperados son `quality`, `infrastructure`, `build` y
`deploy-kind`. `deploy-gke` aparecerá omitido mientras no lo habilites.

Descarga los artefactos de calidad, seguridad y Kubernetes. Verifica que la imagen se publicó
en Packages/GHCR y cambia su visibilidad a pública para permitir acceso al evaluador.
No entregues como final el ZIP inicial sin incorporar las evidencias reales del pipeline.

## 4. Cloud, si decidimos ir por los puntos extra

La guía `GCP.md` incluye Terraform y variables para activar GKE. Requiere un proyecto de GCP con
facturación. Primero completa el flujo sin cloud; luego aprovisiona y adjunta `apply`/`output` reales.

## 5. Apagar el entorno local

```powershell
docker compose down
```

Esto conserva los datos. Agregar `-v` elimina el volumen y la base de datos local.
