import os
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from rich.console import Console

class ActionableClassifier:
    """
    Classifies text as actionable (command/request) or non-actionable (statement/question)
    """
    def __init__(self, model_path="./src/gating_classifiers/models/mobilebert-finetuned-actionable"):
        """
        Initialize the actionable classifier with a fine-tuned MobileBERT model
        
        Args:
            model_path: Path to the model directory
        """
        self.console = Console()
        self.model_path = model_path
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        try:
            self.console.print("[bold cyan]Loading MobileBERT classifier...[/bold cyan]")
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_path)
            self.model.to(self.device)
            self.model.eval()
            self.console.print("[bold green]MobileBERT classifier loaded successfully[/bold green]")
        except Exception as e:
            self.console.print(f"[bold red]Error loading MobileBERT model: {e}[/bold red]")
            self.tokenizer = None
            self.model = None
    
    def is_actionable(self, text, threshold=0.5):
        """
        Classifies if the text is actionable or not
        
        Args:
            text: Text to classify
            threshold: Confidence threshold for actionable classification
            
        Returns:
            dict: Classification results including prediction and confidence
        """
        if not self.model or not self.tokenizer:
            return {"text": text, "prediction": "Non-actionable", "confidence": 0.0, "actionable": False}
        
        try:
            inputs = self.tokenizer(text, return_tensors="pt", truncation=True, 
                               padding=True, max_length=128).to(self.device)
            
            with torch.no_grad():
                outputs = self.model(**inputs)
            
            probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)
            prediction = torch.argmax(probabilities, dim=-1).item()
            confidence = probabilities[0][prediction].item()
            
            is_actionable = prediction == 1 and confidence >= threshold
            
            return {
                "text": text,
                "prediction": "Actionable" if prediction == 1 else "Non-actionable",
                "confidence": confidence,
                "actionable": is_actionable
            }
        except Exception as e:
            self.console.print(f"[bold red]Error during classification: {e}[/bold red]")
            return {"text": text, "prediction": "Non-actionable", "confidence": 0.0, "actionable": False} 