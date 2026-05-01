def judge_answer(predicted, ground_truth):
    return "PASS" if ground_truth.lower() in predicted.lower() else "FAIL"