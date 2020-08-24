def format_table(data, headers):
    header_count = len(headers)
    column_lengths = tuple(
        max(
            len(headers[column_number]),
            max(len(row[column_number]) for row in data)
        )
        for column_number in range(header_count)
    )
    header_padding = tuple(
        " " * (column_lengths[column_number] - len(headers[column_number]) + 4)
        for column_number in range(header_count)
    )
    table = "```CSS\n{}```".format(
        "".join(headers[n] + header_padding[n] for n in range(header_count))
    )
    items = "\n".join(
        " :: ".join(
            element +
            " " * (column_lengths[column] - len(element).replace("​", ""))
            for column, element in enumerate(row)
        )
        for row in data
    )
    table += "```asciidoc\n{}```".format(items)
    return table
