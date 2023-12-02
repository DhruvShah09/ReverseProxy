from fastapi import FastAPI, HTTPException
import subprocess
import fileinput

app = FastAPI()

NGINX_CONFIG_FILE = "/etc/nginx/sites-enabled/fastapi_nginx"

@app.post("/reload-nginx")
async def reload_nginx(request_body: dict):
    # Assuming request_body contains the new proxy data
    new_proxy_data = request_body.get("new_proxy_data")

    if not new_proxy_data:
        raise HTTPException(status_code=400, detail="Missing 'new_proxy_data' in request body")

    try:
        # Replace the IP and port in the Nginx configuration file
        replace_proxy_data(new_proxy_data)

        # Send HUP signal to Nginx master process
        file = open("/var/run/nginx.pid", "r")
        pid = file.read().strip()
        subprocess.run(["sudo", "kill", "-HUP", pid], check=True)

        return {"message": "Nginx reloaded successfully"}
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Failed to reload Nginx: {e}")

def replace_proxy_data(new_proxy_data):
    with fileinput.FileInput(NGINX_CONFIG_FILE, inplace=True, backup=".bak") as file:
        for line in file:
            if "proxy_pass" in line:
                # Replace the IP and port in the proxy_pass line
                line = f"        proxy_pass http://{new_proxy_data};\n"
            print(line, end='')

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
