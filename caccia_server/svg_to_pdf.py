import xml.etree.ElementTree as ET
import cairosvg
import tempfile
import os
import re

def create_certificate_pdf(username, template_path):
    """
    Flask-compatible function that creates a certificate PDF with the given username.
    Uses the provided template path and creates a temporary PDF file.
    
    Args:
        username (str): Username to put on the certificate
        template_path (str): Path to the SVG template file
        
    Returns:
        str: Path to the temporary PDF file
        
    Raises:
        Exception: If SVG template not found or PDF generation fails
    """
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"SVG template not found at: {template_path}")
    
    # Create temporary PDF file
    temp_pdf = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
    temp_pdf_path = temp_pdf.name
    temp_pdf.close()
    
    try:
        # Process the SVG and generate PDF
        _modify_svg_and_export_pdf(template_path, username, temp_pdf_path)
        return temp_pdf_path
    except Exception as e:
        # Clean up temp file if creation failed
        if os.path.exists(temp_pdf_path):
            os.unlink(temp_pdf_path)
        raise e

def _modify_svg_and_export_pdf(input_svg_path, new_username, output_pdf_path):
    """
    Internal function that processes the SVG template and exports to PDF.
    """
    # Read the SVG file
    with open(input_svg_path, 'r', encoding='utf-8') as file:
        svg_content = file.read()
    
    # Find and replace the text content of the username element
    # First try: Look for text directly in the <text> element with id="username"
    direct_text_pattern = r'(<text[^>]*id="username"[^>]*>)([^<]*)(</text>)'
    match = re.search(direct_text_pattern, svg_content, re.DOTALL)
    
    if match:
        old_text = match.group(2)
        print(f"Found current username (direct text): '{old_text.strip()}'")
        # Replace the text content
        modified_svg = re.sub(direct_text_pattern, rf'\g<1>{new_username}\g<3>', svg_content, flags=re.DOTALL)
        print(f"Updated username to: '{new_username}'")
    else:
        # Fallback: Look for text in tspan element within element with id="username"
        tspan_pattern = r'(<text[^>]*id="username"[^>]*>.*?<tspan[^>]*>)([^<]*)(</tspan>)'
        match = re.search(tspan_pattern, svg_content, re.DOTALL)
        
        if match:
            old_text = match.group(2)
            print(f"Found current username (tspan): '{old_text.strip()}'")
            # Replace the text content
            modified_svg = re.sub(tspan_pattern, rf'\g<1>{new_username}\g<3>', svg_content, flags=re.DOTALL)
            print(f"Updated username to: '{new_username}'")
        else:
            print("Warning: Could not find element with id='username'")
            modified_svg = svg_content
    
    # Write modified SVG to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.svg', delete=False, encoding='utf-8') as temp_svg:
        temp_svg.write(modified_svg)
        temp_svg_path = temp_svg.name
    
    try:
        # Convert SVG to PDF using cairosvg
        cairosvg.svg2pdf(url=temp_svg_path, write_to=output_pdf_path)
        print(f"PDF exported successfully to: {output_pdf_path}")
        
    except Exception as e:
        print(f"Error converting to PDF: {e}")
        raise e
    
    finally:
        # Clean up temporary SVG file
        if os.path.exists(temp_svg_path):
            os.unlink(temp_svg_path)