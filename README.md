# Run n8n
```bash
docker run -it --rm --name n8n \
	--network=host \
	-p 5678:5678 \
	-e WEBHOOK_URL=https://snipe-related-possibly.ngrok-free.app \
	-e N8N_HOST="snipe-related-possibly.ngrok-free.app" \
	-e N8N_PROTOCOL=https \
	-v n8n_data:/home/node/.n8n \
	docker.n8n.io/n8nio/n8n
```

# Run ngrok
```bash
ngrok http --url=snipe-related-possibly.ngrok-free.app 5678
```
# Set up webhook URL for the telegram bot
```bash
curl -X POST "https://api.telegram.org/bot<token>/setWebhook" \
     -d "url=https://snipe-related-possibly.ngrok-free.app/webhook-test/1400e110-bcce-4de7-9c6f-9d74479b12c3/webhook"
```
# Run the simulate service
```bash
python voffice_service.py
python sapp_service.py
```
