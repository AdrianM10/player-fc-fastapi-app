from fastapi import FastAPI
from mangum import Mangum

app = FastAPI()
handler = Mangum(app)


@app.get("/")
def root():
    return {"statusCode": 200, "body": "Hello Player! Welcome To The Beautiful Game"}
