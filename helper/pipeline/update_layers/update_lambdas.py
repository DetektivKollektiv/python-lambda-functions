import boto3
import traceback

try:
    lc = boto3.client('lambda')
    response = lc.list_layers()
    # Get all layers
    layers = response['Layers']
    # Find relevant layer

    # Get all lambda functions
    response = lc.list_functions(MaxItems=500)
    lambdas = response['Functions']

    for layer in layers:
        relevant_lambdas = []
        for l in lambdas:
            if 'Layers' in l:
                for lambda_layer in l['Layers']:
                    lambda_layer['CleanArn'] = lambda_layer['Arn'].rsplit(':', 1)[
                        0]
                    # If the function uses the current layer
                    if lambda_layer['CleanArn'] == layer['LayerArn']
                    # If the function is not up to date
                    if lambda_layer['Arn'] != layer['LatestMatchingVersion']['LayerVersionArn']:
                        # Update Arn and add lambda to be updated
                        lambda_layer['Arn'] = layer['LatestMatchingVersion']['LayerVersionArn']
                        relevant_lambdas.append(l)

        # Update config of all lambdas
        for lambda_function in relevant_lambdas:
            new_layer_arns = []
            for layer in lambda_function['Layers']:
                new_layer_arns.append(layer['Arn'])
            lc.update_function_configuration(
                FunctionName=lambda_function['FunctionName'],
                Layers=new_layer_arns)

except:
    print(traceback.format_exc())
