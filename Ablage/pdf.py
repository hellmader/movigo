from fpdf import FPDF

pdf = FPDF('P', 'mm', 'A4')
pdf.add_page()
pdf.set_font("Arial",size=12)
pdf.cell(200,10,txt="Hello world")
pdf.output("/home/hell/test.pdf")
