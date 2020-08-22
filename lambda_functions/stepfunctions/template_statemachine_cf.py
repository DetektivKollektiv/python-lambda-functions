import argparse
import sys
import json


def read_sm_def(
        sm_def_file: str
) -> str:
    """
    Reads state machine definition from a file and returns it as a dictionary.

    Parameters:
        sm_def_file (str) = the name of the state machine definition file.

    Returns:
        sm_def_str (str) = the state machine definition as str.
    """

    try:
        with open(f"{sm_def_file}", "r") as f:
            return f.read()
    except IOError as e:
        print("Path does not exist!")
        print(e)
        sys.exit(1)


def template_state_machine(
        template_in_file: str,
        sm_def: str
) -> str:
    """
    Templates out the CloudFormation for creating a state machine.

    Parameters:
        template_in_file (str) = template.yaml
        sm_def (str) = a dictionary definition of the aws states language state machine.

    Returns:
        templated_cf (str) = template.yaml appended with a definition of the state machine.
    """

    try:
        with open(f"{template_in_file}", "r") as f:
            template_out_str = f.read()
    except IOError as e:
        print("Path does not exist!")
        print(e)
        sys.exit(1)

    templated_cf = "\n" + \
                   "  StateMachineLambdaRole:\n" + \
                   "    Type: AWS::IAM::Role\n" + \
                   "    Properties:\n" + \
                   "      AssumeRolePolicyDocument:\n" + \
                   "        Statement:\n" + \
                   "        - Effect: Allow\n" + \
                   "          Principal:\n" + \
                   "            Service: [states.amazonaws.com]\n" + \
                   "          Action: sts:AssumeRole\n" + \
                   "      Policies:\n" + \
                   "      - PolicyName: !Sub 'States-Lambda-Execution-DetektivKollektiv-Policy-${STAGE}'\n" + \
                   "        PolicyDocument:\n" + \
                   "          Statement:\n" + \
                   "          - Effect: Allow\n" + \
                   "            Action:\n" + \
                   "            - logs:CreateLogStream\n" + \
                   "            - logs:CreateLogGroup\n" + \
                   "            - logs:PutLogEvents\n" + \
                   "            Resource: '*'\n" + \
                   "          - Effect: Allow\n" + \
                   "            Action:\n" + \
                   "            - lambda:InvokeFunction\n" + \
                   "            Resource: '*'\n" + \
                   "  SearchFactCheckStepFunction:\n" + \
                   "    Type: AWS::StepFunctions::StateMachine\n" + \
                   "    Properties:\n" + \
                   "      DefinitionString: !Sub |\n" + sm_def + "\n" + \
                   "      RoleArn:\n" + \
                   "        Fn::GetAtt:\n" + \
                   "        - StateMachineLambdaRole\n" + \
                   "        - Arn\n" + \
                   "      StateMachineName: !Sub 'SearchFactChecks-${STAGE}'\n"

    return template_out_str + templated_cf


# Initiate the parser
parser = argparse.ArgumentParser(description="This program appends a stepfunction definition to template.yaml")
parser.add_argument('--smdef', help="State machine definition", default='sm_def.json')
parser.add_argument('--intemplate', help="Input template.yaml", default='intemplate.yaml')
parser.add_argument('--outtemplate', help="Output template.yaml", default=sys.stdin)
# Read arguments from the command line
args = parser.parse_args()

# Read the definition of the step function
sm_def_dict = read_sm_def(
    sm_def_file=args.smdef
)

print(sm_def_dict)

cfm_sm_def = template_state_machine(
    template_in_file=args.intemplate,
    sm_def=sm_def_dict
)

with open(args.outtemplate, "w") as f:
    f.write(cfm_sm_def)
