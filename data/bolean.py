import csv

input_file = 'animais.csv'
output_file = 'saida1.csv'

with open(input_file, mode='r', newline='', encoding='utf-8') as infile, \
     open(output_file, mode='w', newline='', encoding='utf-8') as outfile:

    reader = csv.reader(infile)
    writer = csv.writer(outfile)

    header = next(reader)
    writer.writerow(header)

    for row in reader:
        new_row = []
        for value in row:
            if value == 'TRUE':
                new_row.append('True')
            elif value == 'FALSE':
                new_row.append('False')
            else:
                new_row.append(value)
        writer.writerow(new_row)
