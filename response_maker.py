from fpdf import FPDF


def create_table(pdf, data, title='', data_size=10, title_size=12, align_data='L', align_header='L',
                 cell_width=(160, 40)):
    line_height = pdf.font_size * 2.5
    col_width = cell_width

    pdf.set_font(size=title_size)
    # add title
    if title != '':
        pdf.multi_cell(0, line_height, title, border=0, align='j', ln=3, max_line_height=pdf.font_size)
        pdf.ln(line_height)  # move cursor back to the left margin

    pdf.set_font(size=data_size)
    pdf.set_x(pdf.l_margin)
    x_left = pdf.get_x()
    x_right = x_left + pdf.epw
    pdf.line(x_left, pdf.get_y(), x_right, pdf.get_y())

    for i in range(len(data)):
        row = data[i]
        for i in range(len(row)):
            datum = row[i]
            if not isinstance(datum, str):
                datum = str(datum)
            adjusted_col_width = int(col_width[i])
            pdf.multi_cell(adjusted_col_width, line_height, datum, border=0, align=align_data, ln=3,
                           max_line_height=pdf.font_size)
        pdf.ln(line_height)  # move cursor back to the left margin
    y3 = pdf.get_y()
    pdf.line(x_left, y3, x_right, y3)
    pdf.ln(line_height)


def make_pdf_from_json(response_json):
    pdf_object = FPDF()
    pdf_object.add_page()
    pdf_object.set_font("Times", size=10)

    # JSONfile formal like data.json

    # with open('stats.json', 'r') as jsonfile:
    #     response_json = json.load(jsonfile)
    for section in response_json['sections']:

        section_header = section['section_header']
        pdf_object.set_font("Times", size=24)
        pdf_object.multi_cell(0, pdf_object.font_size * 2.5, section_header, border=0, align='j', ln=3,
                              max_line_height=pdf_object.font_size)
        pdf_object.ln(pdf_object.font_size * 2.5)

        for table_info in section['tables']:
            pdf_object.set_font("Times", size=10)
            header = table_info['table_header']
            data = table_info['table']
            create_table(pdf_object, get_reformated_data(data), header)
            pdf_object.ln(3)
        pdf_object.add_page()

    pdf_object.output('table_function.pdf')


def get_reformated_data(data):
    reformated_data = []
    for k, v in data.items():
        reformated_data.append([k, v])
    return reformated_data


def main():
    make_pdf_from_json()


if __name__ == '__main__':
    main()
