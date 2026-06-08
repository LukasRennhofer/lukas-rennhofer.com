import html

def generate_html(tokens):

    result = []

    for token in tokens:

        text = html.escape(token.text)

        if token.kind == "text":
            result.append(text)
            continue

        result.append(
            f'<span class="{token.kind}">{text}</span>'
        )

    return f"""<!DOCTYPE html>
<div class="code-box">
<pre><code>
{''.join(result)}
</code></pre>
</div>
"""
