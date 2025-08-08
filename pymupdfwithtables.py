import pymupdf
from deep_translator import GoogleTranslator

 # Define color "white"
WHITE = pymupdf.pdfcolor["white"]

 # This flag ensures that text will be dehyphenated after extraction.
textflags = pymupdf.TEXT_DEHYPHENATE

# Configure the desired translator
to_english = GoogleTranslator(source="de", target="en")

 # Open the document
doc = pymupdf.open(r"data/8424983_H932.EUR92299.9000507723.20250611.CTS01.PDF")

# Define an Optional Content layer in the document named "Korean".
 # Activate it by default.
ocg_xref = doc.add_ocg("English", on=True)


def extract_text():
    global bbox
    # Extract text grouped like lines in a paragraph.
    blocks = page.get_text("blocks", flags=textflags)
    # Every block of text is contained in a rectangle ("bbox")
    for block in blocks:
        bbox = block[:4]  # area containing the text
        german = block[4]  # the text of this block

        # Invoke the actual translation to deliver us a Korean string
        english = to_english.translate(german)

        # Cover the English text with a white rectangle.
        page.draw_rect(bbox, color=None, fill=WHITE, oc=ocg_xref)

        # Write the Korean text into the rectangle
        page.insert_htmlbox(bbox, english, oc=ocg_xref)


# Iterate over all pages
for page_num in range(len(doc)):
     page = doc.load_page(page_num)
     #extract_text()
     processed_table_bboxes = []
     table_finder_obj = page.find_tables(strategy="text",
    vertical_strategy="text",
    horizontal_strategy="lines",
    snap_tolerance=3,
    join_tolerance=5)
     tables = list(table_finder_obj)
     if tables:
         print(f"  Found {len(tables)} table(s) on page {page_num + 1}.")

     for table in tables:
         # Add the table's overall bounding box to our list
         processed_table_bboxes.append(table.bbox)
         full_text=table.extract();
         print('fulle table',full_text)
         rows=table.rows
         print('rows',rows)
         row_num =0
         for row in table.extract():
           row_b=rows[row_num]
           row_num+=1
           cell_num=0
           for cell in row:
             cell_bbox=row_b.cells[cell_num]
             original_text = cell

             # cell_info is a tuple: (x0, y0, x1, y1, text)
             # Only translate if the cell contains actual text
             if original_text and original_text.strip():
                 try:
                     translated_text = to_english.translate(original_text)
                     print(translated_text)
                     # Clear the original text area by filling it with white.
                     # This effectively "erases" the old text.
                     page.draw_rect(cell_bbox, color=None, fill=WHITE, oc=ocg_xref)

                     # Insert the translated text into the original cell's bounding box.
                     # insert_htmlbox is good for fitting text within a given rectangle,
                     # handling basic text wrapping if needed.
                     page.insert_htmlbox(cell_bbox, translated_text)
                 except Exception as e:
                     print(
                         f"    Error translating table cell on page {page_num + 1} (text: '{original_text[:50]}...'): {e}")
                     # If translation fails, still clear the original text to avoid mixed languages
                     #page.draw_rect(cell_bbox, color=None, fill=pymupdf.pdfcolor['white'])
                     # Optionally, you could insert the original text back here if translation is critical
                     # page.insert_htmlbox(bbox, original_text)

doc.save("orca-korean_table.pdf")