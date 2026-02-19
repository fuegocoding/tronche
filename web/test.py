from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn

app = FastAPI()

@app.websocket("/ws/draw")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("iPad connected.")
    try:
        while True:
            # This waits silently until the iPad sends a coordinate
            data = await websocket.receive_json()
            
            # This is where you'll eventually feed the math to the neural network
            print(f"Received raw input: {data}")
            
            # For now, just send a dummy guess back to the iPad to prove the loop works
            await websocket.send_text("guess: 🐢")
            
    except WebSocketDisconnect:
        print("iPad disconnected.")

if __name__ == "__main__":
    # Runs the server on your local network on port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)