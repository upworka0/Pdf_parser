import argparse
import os
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO


class PDFParse:
    pdf_path = None
    csv_path = None
    header_data = ""
    rows_data = []
    in_header = False
    file = None

    def __init__(self):
        self.arg_parse()
        pass

    def arg_parse(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--pdf', type=str, required=True)
        parser.add_argument('--csv', type=str, required=True)
        args = parser.parse_args()
        self.pdf_path = args.pdf
        self.csv_path = args.csv

    def file_exist(self, file_path):
        if os.path.exists(file_path):
            return True
        return False

    def get_csv_header(self):
        key_arr = [
            "Price ranges",
            "ADNT_0_10",
            "ADNT_10_80",
            "ADNT_80_600",
            "ADNT_600_2000",
            "ADNT_2000_9000",
            "ADNT_9000+"
        ]

        return ",".join(key_arr) + "\n"

    def check_or_create_dir(self, path):
        if not (os.path.exists(os.path.dirname(path))):
            os.mkdir(os.path.dirname(path))


    def CR_Header_Row(self, header_data):
        """
        Writes header row to putput file
        :param header_data: str , i.e. "field1. field2, field3..."
        """
        self.check_or_create_dir(self.csv_path)
        self.file = open(self.csv_path, "w", encoding="utf-8")
        self.file.write(header_data)
        # self.in_header = False


    def CR_Data_Row(self, row_data):
        """
        Writes data row to destination file
        :param row_data: str, i.e. "GTE,0,0,1..."
        """
        self.check_or_create_dir(self.csv_path)

        self.file.write(row_data)

    def convert_pdf_to_txt(self, path):
        """
        Parse PDF to text
        """
        rsrcmgr = PDFResourceManager()
        retstr = StringIO()
        laparams = LAParams()
        device = TextConverter(rsrcmgr, retstr, codec='utf-8', laparams=laparams)
        fp = open(path, 'rb')
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        pagenos = set()
        first = True

        for page in PDFPage.get_pages(fp, pagenos, caching=True, check_extractable=True):
            if first:
                first = False
                continue
            interpreter.process_page(page)

        text = retstr.getvalue()

        fp.close()
        device.close()
        retstr.close()
        return text

    def adjust_data(self, arr, row_cnt):
        """
            Get csv_data from array
        """
        data = []
        col_cnt = int(len(arr) / row_cnt)

        for i_col in range(col_cnt):
            data.append(arr[i_col * row_cnt:row_cnt * (i_col + 1)])

        csv_data = []
        for i_row in range(row_cnt):
            row_data = []
            for i_col in range(col_cnt):
                row_data.append(data[i_col][i_row])
            csv_data.append(row_data)

        return csv_data

    def get_values_array(self, text):
        """
            Parse text to array
        """
        arr = text.split('\n\n')
        arr = arr[:len(arr)-4]
        arr = [val.strip() for val in arr]
        data = []
        for val in arr:
            if val != '':
                data.append(val)

        row_cnt = 0
        for index, item in enumerate(data):
            if item == 'ANNEX':
                row_cnt = index - 1

        data.remove('Tick Size Table')
        data.remove('ANNEX')

        table_data = []
        for ind in range(len(data)-1, -1, -1):
            try:
                float(data[ind])
                table_data.append(data[ind])
            except:
                break
        table_data.reverse()
        table_data = data[1:row_cnt+1] + table_data
        return self.adjust_data(table_data, row_cnt)

    def parse(self):
        """
        Parse PDF to array data
        """
        if not self.file_exist(self.pdf_path):
            print("PDF file `%s` doesn't exist" % self.pdf_path)
        else:
            json_data = self.get_values_array(self.convert_pdf_to_txt(self.pdf_path))
            for index1 in range(1, len(json_data)):
                row = json_data[index1]
                text = ""
                for index2 in range(0, len(row)):
                    text = text + row[index2] + ","
                self.rows_data.append(text[:len(text) - 1] + "\n")

    def to_csv(self):
        """
        Store data to csv
        """
        self.header_data = self.get_csv_header()
        self.CR_Header_Row(self.header_data)

        for row in self.rows_data:
            self.CR_Data_Row(row)
        self.file.close()

    """
    Test Case
    """
    def test(self):
        self.pdf_path = "test.pdf"
        self.csv_path = "test/test.csv"
        self.parse()
        self.to_csv()


parser = PDFParse()
parser.parse()
parser.to_csv()

## for testing
# parser.test()