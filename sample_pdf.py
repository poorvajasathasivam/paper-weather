# create_sample_pdf.py
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

def create_sample_pdf(output_path):
    """Create a sample PDF with climate change information."""
    c = canvas.Canvas(output_path, pagesize=letter)
    
    # Set font and size
    c.setFont("Helvetica", 12)
    
    # Add a title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(72, 750, "Climate Change Information Document")
    
    # Add content
    c.setFont("Helvetica", 12)
    y_position = 720
    
    paragraphs = [
        "Climate change refers to long-term shifts in temperatures and weather patterns. These shifts may be natural, such as through variations in the solar cycle. But since the 1800s, human activities have been the main driver of climate change, primarily due to burning fossil fuels like coal, oil and gas, which produces heat-trapping gases.",
        "",
        "Key Facts about Climate Change:",
        "1. The Earth's average temperature has increased by about 1.1°C since the pre-industrial era.",
        "2. Carbon dioxide levels in the atmosphere are higher than at any point in the last 800,000 years.",
        "3. The rate of sea level rise has doubled from 1.4 mm per year throughout most of the 20th century to 3.6 mm per year from 2006-2015.",
        "4. The Arctic is warming about twice as fast as the global average.",
        "",
        "Impacts of Climate Change:",
        "- More frequent and intense drought, storms, heat waves, rising sea levels, and melting glaciers",
        "- Oceans are warming, becoming more acidic, and losing oxygen",
        "- Plants and animals are migrating to higher elevations or toward the poles",
        "- Some species are at increased risk of extinction",
        "- Food security threatened in many regions",
        "",
        "Mitigation Strategies:",
        "- Transition to renewable energy sources (solar, wind, hydro)",
        "- Improve energy efficiency in buildings, transportation, and industry",
        "- Protect and restore forests and other carbon sinks",
        "- Develop sustainable agriculture practices",
        "- Implement carbon pricing mechanisms",
        "",
        "The Paris Agreement, adopted in 2015, aims to limit global warming to well below 2°C, preferably to 1.5°C, compared to pre-industrial levels. Countries submit national climate action plans called Nationally Determined Contributions (NDCs).",
        "",
        "Recent studies show that to meet the 1.5°C target, global carbon emissions need to be reduced by 45% from 2010 levels by 2030 and reach 'net zero' by 2050."
    ]
    
    for paragraph in paragraphs:
        if paragraph == "":
            y_position -= 15  # Add extra space for empty lines
        else:
            text_object = c.beginText(72, y_position)
            text_object.setFont("Helvetica", 12)
            text_object.textLine(paragraph)
            c.drawText(text_object)
            y_position -= 15
    
    # Save the PDF
    c.save()

if __name__ == "__main__":
    # Get the app/data/documents directory
    documents_dir = os.path.join("app", "data", "documents")
    
    # Create the directory if it doesn't exist
    os.makedirs(documents_dir, exist_ok=True)
    
    # Create the sample PDF
    output_path = os.path.join(documents_dir, "climate_change_info.pdf")
    create_sample_pdf(output_path)
    
    print(f"Sample PDF created at: {output_path}")