# Arcade Data Parser

A Python solution for parsing Arcade JSON data to extract user interactions and generate human-friendly summaries.

## Features

✅ **Identify User Interactions**: Extracts and lists all user actions in human-readable format  
✅ **AI-Powered Summaries**: Uses OpenAI GPT-4 to generate intelligent, context-aware summaries  
✅ **Social Media Image Generation**: Creates promotional images using DALL-E 3 based on analyzed data  
✅ **JSON File Processing**: Direct parsing from JSON files  
✅ **Detailed Analysis**: Provides event counts, flow names, and contextual information  
✅ **Fallback Support**: Gracefully handles API failures with local summary generation  
✅ **Customizable Prompts**: Easy-to-modify system prompts for both summaries and image generation  

## Usage

### Command Line Interface

```bash
python analyze_arcade.py <json_file> [--generate-image]
```

### Examples

```bash
# Basic analysis
python analyze_arcade.py example_data.json

# Analysis with social media image generation
python analyze_arcade.py example_data.json --generate-image
```

### Programmatic Usage

```python
from arcade_parser import parse_arcade_data
import json

# Load your JSON data
with open('your_data.json', 'r') as f:
    json_data = f.read()

# Parse the data
result = parse_arcade_data(json_data)

# Access results
interactions = result['user_interactions']
summary = result['summary']

# Generate social media image
result_with_image = parse_arcade_data(json_data, generate_image=True)
image_path = result_with_image.get('social_media_image')
```

## Output Format

The parser generates two main outputs:

### 1. User Interactions List
- Human-readable action descriptions
- Examples: "Clicked on button: 'Add to cart'", "Searched for 'scooter'"

### 2. AI-Generated Human-Friendly Summary
- Intelligent analysis of user behavior using OpenAI GPT-4
- Context-aware summaries that understand user intent
- Natural language descriptions of user goals and actions
- Automatic fallback to rule-based summaries if AI is unavailable

### 3. Social Media Promotional Images
- AI-generated promotional images using DALL-E 3
- Product-focused designs with discount/promotional elements
- Optimized for social media engagement
- Automatically incorporates product details and branding

## Example Output

```
============================================================
ARCADE DATA ANALYSIS
============================================================

📊 Flow Name: Add a Scooter to Your Cart on Target.com
📈 Total Events: 11
📋 Total Steps: 13

🎯 USER INTERACTIONS:
----------------------------------------
 1. Clicked on other: 'search'
 2. Typed text (duration: 985ms)
 3. Scrolled page (duration: 5851ms)
 4. Clicked on image: 'Razor A5 Lux 2 Wheel Kick Scooter'
 5. Clicked on button: 'Add to cart'
 ...

📝 AI-GENERATED SUMMARY:
----------------------------------------
The user visited www.target.com with the intention of purchasing a scooter. 
They searched for a scooter, spent time scrolling through options before 
selecting the 'Razor A5 Lux 2 Wheel Kick Scooter', choosing it in both 
blue and pink colors, and added it to their cart. They declined additional 
coverage and confirmed a quantity of one, indicating they were focused on 
a straightforward purchase without extra add-ons.

🎨 SOCIAL MEDIA IMAGE:
----------------------------------------
Generated promotional image: social_media_promotion.png
```

## Generated Social Media Image

Here's an example of the AI-generated promotional image created from the analyzed flow data using the external prompt system:

![Social Media Promotion](./social_media_promotion.png)

*AI-generated promotional image featuring the Razor A5 Lux 2 Wheel Kick Scooter with enhanced polished text overlays, created using external prompts from `prompts.txt` for maximum customizability.*

### Current Image Features:
- **🏆 Mega Badge**: "15% OFF" (120px, top-left)
- **💎 Premium Product**: "Razor Scooter" (72px, center-top)  
- **⚡ Power Button**: "Shop Now" (84px, center-bottom)
- **🫧 Dynamic Bubble**: "Limited Time" (48px, top-right)
- **✨ Elegant Tagline**: "Blue or Pink" (42px, right-center)
- **🎯 Modern Accent**: "Top Rated" (38px, left-center)
- **🏢 Signature Brand**: "TARGET" (32px, bottom-right)

## Data Structure Support

The parser handles the standard Arcade data format with:
- `capturedEvents`: Click, typing, scrolling, and dragging events
- `steps`: Flow steps with page context and interaction details
- `name`: Flow title for context
- Page contexts for website identification
- Search term extraction from URLs

## Files

- `arcade_parser.py`: Core parsing logic and ArcadeParser class with OpenAI integration
- `analyze_arcade.py`: Command-line interface
- `prompts.txt`: External configuration file containing image generation and text overlay prompts
- `example_data.json`: Sample Arcade data for testing
- `social_media_promotion.png`: Generated promotional image example
- `requirements.txt`: Python dependencies including OpenAI, python-dotenv, and Pillow
- `.env.example`: Template for environment variables
- `.env`: Your actual environment variables (not included in git)
- `.gitignore`: Git ignore file to exclude sensitive files
- `README.md`: This documentation

## Configuration

### Summary Parsing Prompt

The system uses OpenAI's GPT model to generate human-friendly summaries. You can customize the prompt used for summary generation by modifying the default prompt below:

**Default System Prompt:**
```
You are an expert at analyzing user behavior data from web interactions. Your task is to create a clear, concise, and human-friendly summary of what a user was trying to accomplish during their session.

Given the following information about a user's session:
- Flow name: {flow_name}
- Website: {website}
- Search terms: {search_terms}
- User interactions: {interactions}

Please generate a summary that:
1. Explains what the user was trying to accomplish
2. Highlights the key actions they took
3. Infers their likely goals or intentions
4. Uses natural, conversational language
5. Keeps the summary to 2-3 sentences maximum

Focus on the user's journey and what they were trying to achieve, not just listing actions.
```

To modify this prompt, edit the `SUMMARY_PROMPT` section in the `arcade_parser.py` file.

### Image Generation System Prompt

The system can generate engaging social media images based on the analyzed user flow data. The image generation uses OpenAI's DALL-E model with prompts loaded from the external `prompts.txt` file:

**Image Generation Approach:**

To ensure 100% reliable and readable text, the system uses a **hybrid two-step approach**:

1. **Clean Product Image**: DALL-E generates a professional product image with NO TEXT
2. **Perfect Text Overlays**: PIL (Python Imaging Library) adds crisp, readable text overlays
3. **Guaranteed Readability**: Text is rendered using system fonts, ensuring perfect clarity

**Generated Text Elements:**
```
Discount Badge: "15% OFF", "20% OFF", or "25% OFF"
Product Name: Shortened product name (e.g., "Razor Scooter")
Urgency Text: "Today Only", "Limited Time", or "Flash Sale"
Call-to-Action: "Shop Now", "Get Yours", or "Buy Today"
Taglines: Product-specific (e.g., "Blue or Pink", "Ride in Style")
Additional: "Free Shipping", "Best Price", "Top Rated"
Branding: Website name in caps (e.g., "TARGET")
```

**Image Generation System Prompt** (from `prompts.txt`):
```
Create a vibrant, professional product showcase image (1024x1024, square format) for {primary_product}.

DESIGN REQUIREMENTS:
- Modern, clean, professional marketing style
- Forward-facing product as the main focal point
- Product should be clearly visible and prominently displayed
- Show the product in an appealing, lifestyle context
- Product variant: {product_details}
- Bright, attention-grabbing background colors
- Leave space around the product for text overlays
- Professional photography style like a high-end retail catalog

IMPORTANT RULES:
- NO TEXT OR WORDS anywhere in the image
- Focus entirely on product presentation
- Clean, uncluttered composition
- High contrast and vibrant colors
- Professional lighting and shadows
- Target audience: people interested in {product_category}

BACKGROUND:
- Colorful gradient or solid background
- Should complement the product colors
- Leave margins around the product for text placement
- Professional marketing aesthetic

Style: High-quality product photography for {website_name} marketing campaign.
```

### Text Overlay System Prompt

**Text Overlay System Prompt** (from `prompts.txt`):
```
ENHANCED POLISHED TEXT OVERLAY SYSTEM

Create sophisticated, integrated text overlays with multiple visual effects using PIL (Python Imaging Library) with multi-layer rendering and intelligent positioning.

🏆 MEGA DISCOUNT BADGE (120px): Extra dramatic impact
   - Red text with golden yellow extra-thick border (6px)
   - Double-layer shadow for dramatic depth
   - Positioned: Top-left, perfectly centered
   - Enhanced impact font with 20% larger sizing

💎 PREMIUM PRODUCT NAME (72px): Sophisticated elegance  
   - Black text with gradient border effect
   - Multi-layer shadow with sophisticated layering
   - Positioned: Center-top for prominence
   - Premium font with refined appearance

🫧 DYNAMIC URGENCY BUBBLE (48px): Animated-like bubbly effect
   - Orange text with dynamic circular border
   - Varying intensity bubble appearance
   - Positioned: Top-right, auto-centered
   - Enhanced bubble effect with larger radius

⚡ POWER CALL-TO-ACTION (84px): 3D button with depth
   - White text on enhanced 3D button background
   - Multi-layer button with gradient effect
   - Positioned: Center-bottom for maximum impact
   - Larger button with extended padding (15px)

✨ ELEGANT TAGLINES (42px): Script-like refinement
   - Brand colors with elegant fade borders
   - Refined shadow with sophisticated layering
   - Positioned: Right-center, auto-balanced
   - Elegant script styling

🎯 MODERN ACCENTS (38px): Contemporary clean styling
   - Clean lines with modern border effects
   - Contemporary shadow with sharp definition
   - Positioned: Left-center for balance
   - Modern font with clean aesthetics

🏢 SIGNATURE BRANDING (32px): Premium subtle elegance
   - Minimal elegant styling with premium effects
   - Subtle border with refined readability
   - Positioned: Bottom-right, professional placement
   - Signature-level subtlety

POSITIONING SYSTEM:
- Intelligent auto-centering based on text dimensions
- Seven strategic zones for optimal visual hierarchy
- Perfect balance with responsive positioning
- Professional text flow and readability

VISUAL EFFECTS:
- Multi-layer rendering (shadow, border, text layers)
- Gradient borders and 3D button effects
- Dynamic bubble effects with varying intensity
- Premium shadows with sophisticated layering
- Enhanced visual impact with dramatic styling
```

**Example Applied Text for Scooter:**
```
✅ Social media image with perfect text saved as: social_media_promotion.png
📝 Applied promotional text:
   Discount: 15% OFF
   Product: Razor Scooter
   Urgency: Flash Sale
   CTA: Get Yours
   Tagline: Blue or Pink
   Extra: Top Rated
   Brand: TARGET
```

**Key Benefits:**
- 🎯 **Perfect Text Clarity**: No more "15 9/6 OE" or distorted characters
- 🎨 **Multi-Layer Rendering**: Shadow, border, and text layers for depth
- 🏆 **Premium Styling**: Mega badges, power buttons, and elegant scripts
- 📏 **Intelligent Centering**: Auto-calculated positioning for perfect balance
- 🔤 **Larger Fonts**: 20-84px fonts for maximum impact and readability
- 🎭 **Interesting Typography**: Varied font styles for visual interest
- 💎 **Sophisticated Effects**: Gradient borders, 3D buttons, and dynamic bubbles
- 🎪 **Seamless Integration**: Text feels naturally woven into the design
- 💪 **Enhanced Visual Impact**: Dramatic shadows and enhanced borders
- 📐 **Strategic Positioning**: Seven intelligent positioning zones
- ✨ **Professional Polish**: Premium appearance with signature-level refinement

### Customizing Prompts

**🔧 How to Modify Prompts:**
- **Image Generation**: Edit the `[IMAGE_GENERATION_PROMPT]` section in `prompts.txt`
- **Text Overlay**: Edit the `[TEXT_OVERLAY_PROMPT]` section in `prompts.txt`  
- **Summary Generation**: Edit the `SUMMARY_PROMPT` variable in `arcade_parser.py`

The system automatically loads prompts from `prompts.txt` on startup. Changes take effect immediately on next run.

### Environment Setup

1. Copy the `.env.example` file to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Add your OpenAI API key to the `.env` file:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

## Requirements

- Python 3.7+
- OpenAI Python library
- python-dotenv for environment variable management

Install dependencies:
```bash
pip install -r requirements.txt
```

## Error Handling

The parser gracefully handles:
- Invalid JSON format
- Missing data fields
- Malformed event structures
- File not found errors

All errors are reported with clear error messages.
