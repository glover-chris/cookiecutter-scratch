#Ask questions based on cookiecutter parameters
def ask_more_questions(question=None):
    try:
        output = input(question)
    except NameError:
        output = raw_input(question)
    return output


if context['framework_to_deploy']=='pyramid':
    deployment_prod_or_dev_file=ask_more_questions('What file you want to deploy: [development.ini] or production.ini :')
    context['deployment_prod_or_dev_file']=(deployment_prod_or_dev_file or 'development.ini')

#Now For every input question from cookiecutter I can do if statements, if a, then b...