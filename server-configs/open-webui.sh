sudo docker run -d \
  -p 3000:8080 \
  --add-host=host.docker.internal:host-gateway \
  -e OPENAI_API_BASE_URL=http://host.docker.internal:8080/v1 \
  -e OPENAI_API_KEY=SECRET_API_KEY \
  -v open-webui:/app/backend/data \
  --name open-webui \
  --restart no \
  ghcr.io/open-webui/open-webui:main