def format_text(text, words_per_line=7, lines_per_page=20):
    words = text.split()
    lines = []
    line = []

    for word in words:
        line.append(word)
        if len(line) == words_per_line:
            lines.append(" ".join(line))
            line = []

    if line:
        lines.append(" ".join(line))

    # Split lines into pages
    pages = []
    for i in range(0, len(lines), lines_per_page):
        pages.append(lines[i:i + lines_per_page])

    return pages