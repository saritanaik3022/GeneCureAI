"""
SQLAlchemy ORM model for On-Target Efficiency Predictions.
"""
from sqlalchemy import Column, String, Float, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import TimeStampedModel


class OnTargetPrediction(TimeStampedModel):
    """
    Stores hybrid ML on-target predictions (CNN + XGBoost + Stacking Ensemble).
    """
    __tablename__ = "on_target_predictions"

    guide_id = Column(String(36), ForeignKey("guide_rnas.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)

    cnn_score = Column(Float, nullable=False)
    xgboost_score = Column(Float, nullable=False)
    ensemble_score = Column(Float, nullable=False)
    feature_vector_105 = Column(JSON, nullable=True)  # List/dict of 105 engineered feature values
    model_version = Column(String(50), default="1.0.0", nullable=False)

    # Relationships
    guide_rna = relationship("GuideRNA", back_populates="on_target_prediction")
