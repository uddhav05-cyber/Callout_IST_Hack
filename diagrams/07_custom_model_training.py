"""
Generate Custom Model Training Architecture Diagram
Shows the training pipeline and continuous learning workflow
"""

from diagrams import Diagram, Cluster, Edge
from diagrams.custom import Custom
from diagrams.onprem.compute import Server
from diagrams.onprem.database import PostgreSQL
from diagrams.onprem.mlops import Mlflow
from diagrams.programming.framework import React
from diagrams.programming.language import Python
from diagrams.aws.ml import Sagemaker

# Custom model training architecture
with Diagram("07 Custom Model Training Pipeline", 
             filename="diagrams/07_custom_model_training",
             show=False,
             direction="TB"):
    
    # User feedback collection
    with Cluster("User Feedback Collection"):
        ui = React("Streamlit UI")
        feedback_db = PostgreSQL("Feedback DB")
        ui >> Edge(label="Store ratings") >> feedback_db
    
    # Training data preparation
    with Cluster("Training Data Preparation"):
        data_collector = Python("Data Collector")
        snli_dataset = Server("SNLI Dataset\n(5,000 examples)")
        user_feedback = Server("User Feedback\n(Verified claims)")
        
        feedback_db >> Edge(label="Export") >> data_collector
        snli_dataset >> Edge(label="Base data") >> data_collector
        user_feedback >> Edge(label="Domain data") >> data_collector
    
    # Training pipeline
    with Cluster("Training Pipeline (2-3 hours)"):
        preprocessing = Python("Preprocessing\n(Tokenization)")
        bart_base = Sagemaker("BART-base\n(140M params)")
        trainer = Mlflow("Hugging Face\nTrainer")
        
        data_collector >> preprocessing
        preprocessing >> Edge(label="Tokenized data") >> trainer
        bart_base >> Edge(label="Fine-tune") >> trainer
    
    # Model evaluation
    with Cluster("Model Evaluation"):
        eval_metrics = Python("Metrics\nCalculation")
        validation = Server("Validation Set\n(1,000 examples)")
        
        trainer >> Edge(label="Evaluate") >> eval_metrics
        validation >> eval_metrics
    
    # Model deployment
    with Cluster("Model Deployment"):
        custom_model = Sagemaker("Custom Model\n(92-93% accuracy)")
        model_registry = Server("Model Registry\n./callout_custom_model/")
        
        eval_metrics >> Edge(label="Save if F1 > threshold") >> custom_model
        custom_model >> Edge(label="Store") >> model_registry
    
    # Production usage
    with Cluster("Production System"):
        nli_engine = Python("NLI Engine")
        pretrained = Server("Pre-trained\nBART (95%)")
        custom = Server("Custom Model\n(92-93%)")
        
        model_registry >> Edge(label="Load") >> nli_engine
        pretrained >> Edge(label="Fallback") >> nli_engine
        custom >> Edge(label="Domain-specific") >> nli_engine
    
    # Continuous learning loop
    nli_engine >> Edge(label="Predictions", style="dashed", color="blue") >> ui
    ui >> Edge(label="User corrections", style="dashed", color="green") >> feedback_db

print("✅ Custom Model Training diagram generated: diagrams/07_custom_model_training.png")
