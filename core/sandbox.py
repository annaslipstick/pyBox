import ast

def run_sandboxed(source_code, api):
    """
    Parses and runs the ISO Python code in a safe environment.
    Expects the ISO to define a 'main(api)' function.
    """
    tree = ast.parse(source_code, filename="<iso>", mode='exec')

    env = {'api': api}  # single globals dict

    # Compile and exec with env as globals and locals
    exec(compile(tree, filename="<iso>", mode='exec'), env, env)

    if 'main' not in env or not callable(env['main']):
        raise RuntimeError("ISO missing required 'main(api)' function")

    env['main'](api)
