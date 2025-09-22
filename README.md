# Arcade Data Parser

A Python solution for parsing Arcade JSON data to extract user interactions and generate human-friendly summaries.

## Features

✅ **Identify User Interactions**: Extracts and lists all user actions in human-readable format  
✅ **AI-Powered Summaries**: Uses OpenAI GPT-4 to generate intelligent, context-aware summaries  
✅ **Social Media Image Generation**: Creates promotional images using GPT-image-1 (newer than DALL-E 3) based on analyzed data  
✅ **JSON File Processing**: Direct parsing from JSON files  
✅ **Detailed Analysis**: Provides event counts, flow names, and contextual information  
✅ **Fallback Support**: Gracefully handles API failures with local summary generation  
✅ **Customizable Prompts**: Easy-to-modify system prompts for both summaries and image generation  

## Usage

### Command Line Interface

```bash
python analyze_arcade.py <json_file>
```

**What it does:**
- Analyzes the Arcade data and displays human-friendly summaries
- **Automatically generates** a promotional social media image using AI (gpt-image-1)
- Saves the image as `social_media_promotion.png` in the current directory

### Examples

```bash
# Analyze data and generate promotional image
python analyze_arcade.py example_data.json --generate-image

# Analyze your own data
python analyze_arcade.py my_arcade_data.json
```

**Output includes:**
- 📊 Flow analysis and event counts
- 🎯 Human-readable user interactions list  
- 📝 AI-generated summary of user intent
- 🎨 **Promotional social media image** (automatically saved)

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
- AI-generated promotional images using GPT-image-1 (newer than DALL-E 3)
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
 6. Clicked on image: 'Blue'
 7. Clicked on image: 'Pink'
 8. Clicked on button: 'Add to cart'
 9. Clicked on button: 'Decline coverage'
10. Clicked on link: '1'
11. Dragged element (duration: 114ms)
12. Started chapter: 'Add a Scooter to Your Cart on Target.com'
13. Interacted on www.target.com - clicked other 'search'
14. Interacted on www.target.com - clicked image 'Razor A5 Lux 2 Wheel Kick Scooter'
15. Interacted on www.target.com - clicked image 'Blue'
16. Interacted on www.target.com - clicked image 'Pink'
17. Interacted on www.target.com - clicked button 'Add to cart'
18. Interacted on www.target.com - clicked button 'Decline coverage'
19. Interacted on www.target.com - clicked link '1'
20. Started chapter: 'Thank you for your interest!'

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

*AI-generated promotional image featuring the Razor A5 Lux 2 Wheel Kick Scooter created using external prompts from `prompts.txt` for maximum customizability.*


## Files

- `arcade_parser.py`: Core parsing logic and ArcadeParser class with OpenAI integration
- `analyze_arcade.py`: Command-line interface
- `prompts.txt`: External configuration file containing image generation prompts
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

The system can generate engaging social media images based on the analyzed user flow data. The image generation uses OpenAI's GPT-image-1 model (newer than DALL-E 3) with prompts loaded from the external `prompts.txt` file:

**Image Generation Approach:**
1. **Integrated Text**: GPT-image-1 generates images with promotional text already integrated
2. **Superior Quality**: Natural-looking text that's part of the image design
3. **Enhanced Readability**: GPT-image-1's advanced text rendering capabilities


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


### Customizing Prompts

**🔧 How to Modify Prompts:**
- **Image Generation**: Edit the `[IMAGE_GENERATION_PROMPT]` section in `prompts.txt`
- **Summary Generation**: Edit the `SUMMARY_PROMPT` variable in `arcade_parser.py`

The system automatically loads prompts from `prompts.txt` on startup. Changes take effect immediately on next run.


### Environment Setup

1. Copy the `.env.example` file to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Add your OpenAI API key and configure feature flags in the `.env` file:
   ```
   # Required: OpenAI API key for AI summaries and image generation
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
