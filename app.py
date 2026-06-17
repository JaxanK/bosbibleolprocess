import streamlit as st
import re
from bs4 import BeautifulSoup

def transform_bible_html(raw_html: str) -> str:
    """
    Parses biblical HTML text, converting ordered lists to styled unordered verse lists,
    and prepending bold numbers to verse items while keeping all inner elements pristine.
    """
    # Use html.parser which comes built-in with Python
    soup = BeautifulSoup(raw_html, "html.parser")
    
    # 1. Target all ordered lists to change them into verse-list groups
    for ol_tag in soup.find_all("ol"):
        # Detect if there's a custom start index, otherwise default to 1
        current_verse_num = int(ol_tag.get("start", 1))
        
        # Transform the <ol> container to <ul class="verse-list">
        ol_tag.name = "ul"
        ol_tag["class"] = "verse-list"
        
        # Clean up the 'start' attribute since it's no longer valid on a <ul>
        if "start" in ol_tag.attrs:
            del ol_tag["start"]
            
        # 2. Iterate through each list item inside this list
        for li_tag in ol_tag.find_all("li", recursive=False):
            # Transform the list item to <li class="verse">
            #li_tag["class"] = "verse"
            
            # Create a brand new <span> tag for our verse counter
            num_tag = soup.new_tag("span")
            num_tag["class"] = "vn"
            num_tag.string = f"{current_verse_num}"


            # Insert 2 spaces (like a tab) before the li elements so they are indented.
            li_tag.insert_before("  ")
            
            # Insert a space at the front of the <li> element (space will not be bolded)
            li_tag.insert(0, " ")

            # Safely insert the number tag at the absolute front of the <li> element
            li_tag.insert(0, num_tag)
            
            # Increment our counter for the next line
            current_verse_num += 1
            
    # Return the modified tree back as a clean string
    return str(soup)


def transform_bible_html_alt_tab(raw_html: str) -> str:
    """
    Parses biblical HTML text, converting ordered lists to styled unordered verse lists,
    and prepending bold numbers to verse items while keeping all inner elements pristine.
    """
    # Use html.parser which comes built-in with Python
    soup = BeautifulSoup(raw_html, "html.parser")
    
    # 1. Target all ordered lists to change them into verse-list groups
    for ol_tag in soup.find_all("ol"):
        # Detect if there's a custom start index, otherwise default to 1
        current_verse_num = int(ol_tag.get("start", 1))
        
        # Transform the <ol> container to <ul class="verse-list">
        ol_tag.name = "ul"
        ol_tag["class"] = "verse-list"
        
        # Clean up the 'start' attribute since it's no longer valid on a <ul>
        if "start" in ol_tag.attrs:
            del ol_tag["start"]
            
        # 2. Iterate through each list item inside this list
        for li_tag in ol_tag.find_all("li", recursive=False):
            # Transform the list item to <li class="verse">
            #li_tag["class"] = "verse"
            
            # Create a brand new <span> tag for our verse counter
            num_tag = soup.new_tag("span")
            num_tag["class"] = "vn"
            num_tag.string = f"{current_verse_num}"


            # Insert space & tab before the li elements so they are indented.
            li_tag.insert_before(" \t")
            
            # Insert a space at the front of the <li> element (space will not be bolded)
            li_tag.insert(0, " ")

            # Safely insert the number tag at the absolute front of the <li> element
            li_tag.insert(0, num_tag)
            
            # Increment our counter for the next line
            current_verse_num += 1
            
    # Return the modified tree back as a clean string
    return str(soup)

def apply_verse_numbering_and_list_conversion(content: str) -> str:
    """
    Applies exactly the three required changes from BOS Prompt #8:
    1. Add bold verse numbers at the start of every <li> verse content
       (with exactly one space after </strong>)
    2. Convert all <ol start="N"> to <ul class="verse-list">
    3. Convert all </ol> to </ul>
    No other modifications are made.
    """
    # Change 2 + 3: Convert ordered lists to unordered lists with the verse-list class
    # Remove any start="X" attribute in the process
    content = re.sub(r'<ol start="\d+">', '<ul class="verse-list">', content)
    content = content.replace('</ol>', '</ul>')

    # Change 1: Add verse numbers
    verse_counter = [1]   # list so it is mutable inside the nested function

    def insert_verse_number(match: re.Match) -> str:
        num = verse_counter[0]
        verse_counter[0] += 1
        # Insert exactly: <strong>N</strong> + one space + original content
        return f"{match.group(1)}<strong>{num}</strong> {match.group(2)}{match.group(3)}"

    # Match every <li>...</li> and number its content
    # Using DOTALL in case any future verse spans lines (current files are single-line)
    content = re.sub(
        r'(<li>)(.*?)(</li>)',
        insert_verse_number,
        content,
        flags=re.DOTALL
    )

    return content

# -- STREAMLIT UI LAYOUT --
st.set_page_config(page_title="Bible HTML Normalizer", layout="wide")

st.title("Scripture Format Normalizer")
st.write("Convert custom raw or ordered lists into semantic structured verse formats safely.")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Input Raw HTML Text")
    user_input = st.text_area("Paste your source text block here:", height=450)

if user_input:
    # Run HTML parser function
    processed_output = transform_bible_html(user_input)
    processed_output2 = transform_bible_html_alt_tab(user_input)
    
    with col2:
        st.subheader("Processed Output Text")
        st.text_area("Copy your modified text here:", value=processed_output, height=450)
        st.subheader("Space & Tab Function Output Text")
        st.text_area("Copy your modified text here:", value=processed_output2, height=450)