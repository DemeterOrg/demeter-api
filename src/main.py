from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def get_root():
    return {
        "Status": "Sucess",
        "Message": "Welcome to FastApi",
    }
