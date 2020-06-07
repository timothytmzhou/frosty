import epicbox


def execute(code):
    files = [{'name': 'main.py', 'content': code.strip().encode()}]
    limits = {'cputime': 60, 'memory': 64}
    result = epicbox.run('python', 'python3 main.py', files=files, limits=limits)
    return result
