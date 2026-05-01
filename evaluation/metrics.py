def compute_cost(tokens, cost_per_1k=0.002):
    return (tokens/1000) * cost_per_1k