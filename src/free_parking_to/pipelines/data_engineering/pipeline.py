from kedro.pipeline import node, Pipeline
from free_parking_to.pipelines.data_engineering.nodes import import_dataset

def create_pipeline(**kwargs):
    return Pipeline (
        [
            node (
                func = import_dataset,
                outputs = "parking",
                name = "extracting xml data",
            )
        ]
    )