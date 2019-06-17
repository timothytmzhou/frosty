#TODO: make this code not look like a 3-year-old vommitted on the floor
def format_table(data):
	lengths = [max(len(row[i]) for row in data) for i in range(4)]
	headers = ["Name", "Description", "Date", "Cost"]
	padding = [" " * (lengths[i] + 4 - len(headers[i])) for i in range(4)]
	formatted = "```CSS\nName{0}Description{1}Date{2}Cost```\n".format(*padding[:4])
	processed = "\n".join(
		"{0} :: {1}    {2}    {3}".format(
			*[row[i] + " " * (lengths[i] - len(row[i])) for i in range(3)], row[3]
		) 
	for row in data)
	formatted += "```asciidoc\n{0}```".format(processed)
	return formatted
