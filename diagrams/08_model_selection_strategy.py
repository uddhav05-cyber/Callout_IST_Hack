"""
Generate Model Selection Strategy Diagram
Shows how the system chooses between pre-trained and custom models
"""

from diagrams import Diagram, Cluster, Edge
from diagrams.onprem.compute import Server
from diagrams.programming.language import Python
from diagrams.aws.ml import Sagemaker

# Model selection strategy
with Diagram("08 Model Selection Strategy", 
             filename="diagrams/08_model_selection_strategy",
             show=False,
             direction="LR"):
    
    # Input
    user_claim = Server("User Input\n(Claim + Evidence)")
    
    # Model selection logic
    with Cluster("Model Selection Engine"):
        selector = Python("Model Selector")
        domain_detector = Python("Domain Detector\n(Politics/Health/etc)")
        
        user_claim >> selector
        user_claim >> domain_detector
        domain_detector >> Edge(label="Domain info") >> selector
    
    # Available models
    with Cluster("Model Registry"):
        pretrained_bart = Sagemaker("Pre-trained BART\n95% accuracy\nGeneral purpose")
        pretrained_mdeberta = Sagemaker("Pre-trained mDeBERTa\n90% accuracy\nMultilingual")
        custom_politics = Sagemaker("Custom: Politics\n93% accuracy\nSpecialized")
        custom_health = Sagemaker("Custom: Health\n94% accuracy\nSpecialized")
        custom_general = Sagemaker("Custom: General\n92% accuracy\nUser-trained")
    
    # Selection logic
    selector >> Edge(label="General domain") >> pretrained_bart
    selector >> Edge(label="Non-English") >> pretrained_mdeberta
    selector >> Edge(label="Politics domain") >> custom_politics
    selector >> Edge(label="Health domain") >> custom_health
    selector >> Edge(label="User feedback") >> custom_general
    
    # Output
    with Cluster("Verification Result"):
        prediction = Python("NLI Prediction")
        confidence = Server("Confidence Score\n+ Model Used")
        
        pretrained_bart >> prediction
        pretrained_mdeberta >> prediction
        custom_politics >> prediction
        custom_health >> prediction
        custom_general >> prediction
        
        prediction >> confidence

print("✅ Model Selection Strategy diagram generated: diagrams/08_model_selection_strategy.png")
