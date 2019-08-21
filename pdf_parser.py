import argparse
import json
import tabula
import os
import re

class PDFParse:
    pdf_path = None
    csv_path = None
    header_data = ""
    rows_data = []
    in_header = False

    def __init__(self):
        self.arg_parse()

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

    def get_key(self, value):
        key = re.sub("\D", "", value)
        key_arr = {
            "010": "ADNT_0_10",
            "1080": "ADNT_10_80",
            "80600": "ADNT_80_600",
            "6002000": "ADNT_600_2000",
            "20009000": "ADNT_2000_9000",
            "9000": "ADNT_9000+"
        }
        if key in key_arr:
            return key_arr[key]
        return value

    def check_or_create_dir(self, path):
        if not (os.path.exists(os.path.dirname(path))):
            os.mkdir(os.path.dirname(path))


    def CR_Header_Row(self, header_data):
        """
        Writes header row to putput file
        :param header_data: str , i.e. "field1. field2, field3..."
        """
        self.check_or_create_dir(self.csv_path)

        if self.in_header and self.file_exist(self.csv_path):
            # read csv all lines and change the header
            with open(self.csv_path, "r", encoding="utf-8") as f:
                data = f.readlines()
            data[0] = header_data

            # write to csv again
            with open(self.csv_path, "w", encoding="utf-8") as f:
                f.writelines(data)
        else:
            # write to csv again
            with open(self.csv_path, "w", encoding="utf-8") as f:
                f.write(header_data)
            self.in_header = False


    def CR_Data_Row(self, row_data):
        """
        Writes data row to destination file
        :param row_data: str, i.e. "GTE,0,0,1..."
        """
        self.check_or_create_dir(self.csv_path)
        with open(self.csv_path, "a", encoding="utf-8") as f:
            f.write(row_data)

    def pdf_to_json(self):
        """
        Convert PDF to JSON
        """
        json_path = "output.json"
        tabula.convert_into(self.pdf_path, json_path, java_options="-Dfile.encoding=UTF8", output_format="json", pages='all')
        return json_path

    def parse(self):
        """
        Parse PDF to array data
        """
        if not self.file_exist(self.pdf_path):
            print("PDF file `%s` doesn't exist" % self.pdf_path)
        else:
            json_path = self.pdf_to_json()

            with open(json_path, "r", encoding="utf-8") as f:
                json_data = json.loads(f.read())

            for index1 in range(1, len(json_data[0]['data'])):
                row = json_data[0]['data'][index1]
                text = ""
                for index2 in range(0, len(row)):
                    if index1 == 1:
                        text = text + self.get_key(row[index2]['text']) + ","
                    else:
                        text = text + row[index2]['text'] + ","

                if index1 == 1:
                    self.header_data = text[:len(text) - 1] + "\n"
                else:
                    self.rows_data.append(text[:len(text) - 1] + "\n")
        os.remove(json_path)

    def to_csv(self):
        """
        Store data to csv
        """
        self.CR_Header_Row(self.header_data)

        for row in self.rows_data:
            self.CR_Data_Row(row)

    """
    Test Case
    """
    def test(self):
        self.pdf_path = "test.pdf"
        self.csv_path = "test/test.csv"
        self.parse()


parser = PDFParse()
parser.parse()
parser.to_csv()
