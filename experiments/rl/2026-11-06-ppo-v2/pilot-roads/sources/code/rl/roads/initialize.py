"""Reuse three constant style-2 inputs for learned road-effect observations."""
import copy
import torch


def fold_constants(state):
    result = {key: value.clone() for key, value in state.items()}
    weight, bias = result['net.0.weight'], result['net.0.bias']
    bias.add_(weight[:, 13:16] @ weight.new_tensor([.5, .5, 1.]))
    weight[:, 13:16].zero_()
    return result


def convert_checkpoint(checkpoint):
    result = copy.deepcopy(checkpoint)
    for name in ('actor', 'critic'):
        result[name] = fold_constants(checkpoint[name])
        optimizer = result[name + '_optimizer']
        first_weight, first_bias = optimizer['param_groups'][0]['params'][:2]
        for key in ('exp_avg', 'exp_avg_sq', 'max_exp_avg_sq'):
            if key in optimizer['state'][first_weight]:
                optimizer['state'][first_weight][key][:, 13:16].zero_()
            if key in optimizer['state'][first_bias]:
                optimizer['state'][first_bias][key].zero_()
    result['pool'] = [fold_constants(state) for state in checkpoint['pool']]
    return result
