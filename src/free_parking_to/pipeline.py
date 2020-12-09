from typing import Dict
from kedro.pipeline import Pipeline
from free_parking_to.pipelines.data_engineering import pipeline as de

def create_pipeline(**kwargs) -> Dict[str, Pipeline]:

    de_pipeline = de.create_pipeline()

    return {
        "de": de_pipeline,
        "__default__": Pipeline([de_pipeline])
    }