from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer
import nltk
nltk.download('punkt_tab')
import PyPDF2
import mysql.connector
from mysql.connector import Error


def insert_into_db(timestamp, filename, summary):
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="MY_PROJECTS"
        )

        if connection.is_connected():
            cursor = connection.cursor()

            # Prepare query
            sql = "INSERT INTO Summariser (ID, FILENAME, SUMMARY) VALUES (%s, %s, %s)"
            cursor.execute(sql, (timestamp, filename, summary))

            connection.commit()

            print("Data inserted successfully!")

    except Error as e:
        print("Error while inserting data:", e)

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def summarize_with_sumy(text, sentence_count=5):
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LexRankSummarizer()
    summary = summarizer(parser.document, sentence_count)
    summarized_text = " ".join(str(sentence) for sentence in summary)
    return summarized_text

def text_extract(file_path):
    with open(file_path, "rb") as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
    return text