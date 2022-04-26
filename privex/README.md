# File Structure

- components/basic: It includes most of the fundamental supporting elements in this framework.
- components/private_ci: Algorithms about the confidence interval for either query-style target (question and influence) and rank target.
- components/private_topk: Algorithms for find the top-k privately.
- core: It wraps up the solutions for four problems. Each solution set has a separate folder, and should follow the meta files in the root.
- framework: It is the main entry of the framework. The meta file includes most of the function calls to the solution set. Each framework implementation is a sub folder.
- evaluation: This folder is deprecated. Please check the folder experiment-2/finding/run.py, experiment-2/finding/measure.py and experiment-2/finding/*.ipynb 
  to see how to evaluate the framework.
