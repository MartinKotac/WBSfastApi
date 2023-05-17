from fastapi import FastAPI
from pydantic import BaseModel, Json
import json

from pipelineMedicineRDF import pipelineRDF

app = FastAPI()


class InputData(BaseModel):
    text: str


class ResponseData(BaseModel):
    rdf_graph: Json


# Define a FastAPI route and the corresponding function to handle the request
@app.post("/predict", response_model=ResponseData)
async def predict(input_data: InputData):
    text = input_data.text
    # Invoke your machine learning script to generate the RDF graph
    rdf_graph = pipelineRDF(text)
    rdf_graph_json = json.dumps(rdf_graph)
    # Construct the response data
    response_data = ResponseData(rdf_graph=rdf_graph_json)
    return response_data
