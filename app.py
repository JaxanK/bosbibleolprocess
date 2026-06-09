import streamlit as st
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
            li_tag["class"] = "verse"
            
            # Create a brand new <strong> tag for our verse counter
            num_tag = soup.new_tag("strong")
            num_tag.string = f"{current_verse_num} "
            
            # Safely insert the number tag at the absolute front of the <li> element
            li_tag.insert(0, num_tag)
            
            # Increment our counter for the next line
            current_verse_num += 1
            
    # Return the modified tree back as a clean string
    return str(soup)

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
    
    with col2:
        st.subheader("Processed Output Text")
        st.text_area("Copy your modified text here:", value=processed_output, height=450)