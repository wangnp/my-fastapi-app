from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def hello_world():
    return {"message": "Hello from FastAPI on Vercel!"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
