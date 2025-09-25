from fastapi import FastAPI, Request, HTTPException, Header

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}