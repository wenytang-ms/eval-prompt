from azure.ai.evaluation._evaluators._common import EvaluatorBase

class SpecEval(EvaluatorBase):
    def __init__(self):
        super().__init__()
    
    @classmethod
    def _compute_spec_score(cls, response: str, ground_truth: str) -> float:
        import re
        import string



    def evaluate(self, **kwargs):
        # Load the output file
        with open(self.output_file, "r", encoding="utf-8") as output_file:
            output_data = output_file.readlines()
        
        # Load the ground truth file
        with open(self.ground_truth_file, "r", encoding="utf-8") as ground_truth_file:
            ground_truth_data = ground_truth_file.readlines()
        
        # Compare the output and ground truth
        for output, ground_truth in zip(output_data, ground_truth_data):
            output = json.loads(output)
            ground_truth = json.loads(ground_truth)
            self.compare(output, ground_truth)
        
        # Return the evaluation result
        return self.result
    
    def compare(response: str, ground_truth: str) -> float:
        import difflib
        # Compute the difference between response and ground_truth
        # Find the starting index of 'openapi' in response and ground_truth
        response_start = response.find('openapi')
        ground_truth_start = ground_truth.find('openapi')

        # If 'openapi' is not found in either string, return 0.0
        if response_start == -1 or ground_truth_start == -1:
            return 0.0

        # Slice the strings from the 'openapi' index
        response = response[response_start:]
        ground_truth = ground_truth[ground_truth_start:]

        # Compute the difference between the sliced response and ground_truth
        diff = difflib.ndiff(response, ground_truth)
        diff_count = sum(1 for d in diff if d.startswith('- ') or d.startswith('+ '))

        # Calculate the ratio of diff bytes to ground truth bytes
        ground_truth_length = len(ground_truth)
        if ground_truth_length == 0:
            return 0.0

        return diff_count / ground_truth_length