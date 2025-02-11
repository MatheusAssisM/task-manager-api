from bson import ObjectId
from ..models.metrics import Metrics


class MetricsRepository:
    def __init__(self, collection):
        self.collection = collection

    def get_metrics(self) -> Metrics:
        metrics_data = self.collection.find_one({})
        return Metrics.from_dict(metrics_data) if metrics_data else Metrics()

    def update_metrics(self, metrics: Metrics) -> None:
        if metrics.id:
            # Convert id to ObjectId if it's a string
            metrics_id = (
                ObjectId(metrics.id) if isinstance(metrics.id, str) else metrics.id
            )
            self.collection.update_one({"_id": metrics_id}, {"$set": metrics.to_dict()})
        else:
            self.collection.insert_one(metrics.to_dict())
