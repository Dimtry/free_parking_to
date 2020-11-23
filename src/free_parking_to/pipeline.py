
from kedro.pipeline import Pipeline
from free_parking_to.data_engineering import pipeline as de

def create_pipeline(**kwargs):

    de_pipeline = de.create_pipeline()

    return {
        "de": de_pipeline,
        "__default__": Pipeline([de_pipeline])
    }