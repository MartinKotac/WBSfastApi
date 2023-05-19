from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from typing import List

from pipelineMedicineRDF import pipelineRDF

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:4200",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Triple(BaseModel):
    subjectRdf: str
    propertyRdf: str
    objectRdf: str


class InputData(BaseModel):
    text: str


class ResponseData(BaseModel):
    rdf_graph: List[Triple]


def extract_triples(rdf_graph_string: str) -> List[Triple]:
    # Split the RDF graph string into separate triples
    triples = rdf_graph_string.strip().split('\n')
    extracted_triples = []
    # Extract subject, predicate, and object from each triple
    for triple in triples:
        parts = triple.strip().split(' ')
        subject = parts[0]
        predicate = parts[1]
        obj = ' '.join(parts[2:])  # Join remaining parts as the object
        extracted_triples.append(Triple(subjectRdf=subject, propertyRdf=predicate, objectRdf=obj))
    return extracted_triples


# Define a FastAPI route and the corresponding function to handle the request
@app.post("/predict", response_model=ResponseData)
async def predict(input_data: InputData):
    text = input_data.text
    # Invoke your machine learning script to generate the RDF graph
    rdf_graph = pipelineRDF(text)
    # Convert the RDF graph to a list of Triple objects
    rdf_graph_triples = extract_triples(rdf_graph)
    response_data = ResponseData(rdf_graph=rdf_graph_triples)
    return response_data