"""
Basic example of a Mkdocs-macros module
"""
from io import StringIO
import sys
import math
import os
# import html

def evalCap(code):
    old_stdout = sys.stdout
    redirected_output = sys.stdout = StringIO()
    exec(code)
    sys.stdout = old_stdout
    return redirected_output.getvalue()



def define_env(env):
    """
    This is the hook for defining variables, macros and filters

    - variables: the dictionary that contains the environment variables
    - macro: a decorator function, to declare a macro.
    """
    # import the predefined macro
    fix_url = env.variables.fix_url # make relative urls point to root

    @env.macro
    def button(label, url):
        "Add a button"
        url = fix_url(url)
        HTML = """<a class='button' href="%s">%s</a>"""
        return HTML % (url, label)

    
    @env.macro
    def code_from_file(fn: str, start: int = None, stop: int = None, flavor: str = "", download=False, execute=False):
        """
        Load code from a file and save as a preformatted code block.
        Start and stop can also be used to indicate the starting line and the stopping line
        you wish to extract from the file. 
        If a flavor is specified, it's passed in as a hint for syntax highlighters.

        Example usage in markdown:

            {{ code_from_file("code/myfile.py", flavor = "python") }}
            {{ code_from_file("code/myfile.py", 2, 5) }}
            {{ code_from_file("code/myfile.py", stop = 5) }}
            {{ code_from_file("code/myfile.py", 2, 5, "python") }}
        """
        docs_dir = env.variables.get("./docs_dir", "docs")
        relative_fn = os.path.join(docs_dir, fn)
        full_fn = os.path.abspath(os.path.join(docs_dir, fn))
        if not os.path.exists(relative_fn):
            return f"""<b>File not found: {fn}</b>"""
        with open(relative_fn, "r") as f:
            fr=str(start or "the beginning")
            to=str(stop or  "the end")
            btn= "" if not download else button("Download this file",fn)
            btn=f"<span class='dlbtn'>{btn}</span>"

            output=f"<div class='codeblock'><div class='codetitle'><code>{os.path.basename(full_fn)} from {fr} to {to} </code> {btn} </div>\n"

            temp = []
            x = f.readlines()
            
            # a fix to change python slicing to code line numbers, includes the final integer now.
            if start is not None and start > 0:
                start = start -1 
            if stop is not None:
                stop = stop + 1
            
            for line in x:
                temp.append(line)

            code="".join(temp[start:stop])
            output+=f"""```python \n{code} \n```\n\n"""
            if execute:
                output+="<div class='codetitle'>Output</div>\n"
                output+=f"""```\n{evalCap(code)}\n```\n\n"""

            output+="\n</div>"
            return output

    @env.macro
    def external_markdown(fn: str):
        """
        Load markdown from files external to the mkdocs root path.
        Example usage in markdown:

            {{external_markdown("../../README.md")}}

        """
        docs_dir = env.variables.get("docs_dir", "docs")
        fn = os.path.abspath(os.path.join(docs_dir, fn))
        if not os.path.exists(fn):
            return f"""<b>File not found: {fn}</b>"""
        with open(fn, "r") as f:
            return f.read()
    
    
    # create a jinja2 filter
    @env.filter
    def reverse(x):
        "Reverse a string (and uppercase)"
        return x.upper()[::-1]
    
    
if __name__=="__main__":
    print(evalCap("print('hello inception')"))
