import os
import yaml

class PromptManager:
    def __init__(self, prompt_file=None):
        # Default to prompts.yaml in the same directory
        if prompt_file is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            prompt_file = os.path.join(base_dir, "prompts.yaml")
        
        self.prompt_file = prompt_file
        self.prompts = self._load_prompts()

    def _load_prompts(self):
        """Loads prompts from the local YAML file."""
        if not os.path.exists(self.prompt_file):
            raise FileNotFoundError(f"Prompts file not found: {self.prompt_file}")
        
        with open(self.prompt_file, 'r') as f:
            return yaml.safe_load(f)

    def get_prompt(self, name: str) -> str:
        """
        Fetches a specific prompt template.
        Future Upgrade: This method will eventually call Langfuse.get_prompt(name)
        """
        if name not in self.prompts:
            raise KeyError(f"Prompt '{name}' not found in configuration.")
        
        # Return the content string
        return self.prompts[name]['content']