#!/usr/bin/env python3
"""
Arcade Data Parser

Parses Arcade JSON data to extract user interactions and generate human-friendly summaries.
"""

import json
import os
import requests
from typing import Dict, List, Any
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
import io

# Load environment variables
load_dotenv()

def load_prompts_from_file(file_path: str = "prompts.txt") -> Dict[str, str]:
    """Load prompts from external configuration file"""
    prompts = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse the prompts file
        current_section = None
        current_prompt = []
        
        for line in content.split('\n'):
            line = line.strip()
            
            # Skip comments and empty lines
            if line.startswith('#') or not line:
                continue
            
            # Check for section headers
            if line.startswith('[') and line.endswith(']'):
                # Save previous section if exists
                if current_section and current_prompt:
                    prompts[current_section] = '\n'.join(current_prompt).strip()
                
                # Start new section
                current_section = line[1:-1]
                current_prompt = []
            else:
                # Add line to current prompt
                if current_section:
                    current_prompt.append(line)
        
        # Save the last section
        if current_section and current_prompt:
            prompts[current_section] = '\n'.join(current_prompt).strip()
            
    except Exception as e:
        print(f"Warning: Could not load prompts from {file_path}: {e}")
        # Fallback to default prompts if file loading fails
        prompts = {
            'IMAGE_GENERATION_PROMPT': 'Create a vibrant, professional product showcase image for {primary_product}.',
            'TEXT_OVERLAY_PROMPT': 'Apply sophisticated text overlays with premium styling.'
        }
    
    return prompts

# Load prompts from external file
PROMPTS = load_prompts_from_file()

# Default summary prompt - can be customized
SUMMARY_PROMPT = """You are an expert at analyzing user behavior data from web interactions. Your task is to create a clear, concise, and human-friendly summary of what a user was trying to accomplish during their session.

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

Focus on the user's journey and what they were trying to achieve, not just listing actions."""

# Image generation and text overlay prompts are now loaded from external prompts.txt file


class ArcadeParser:
    """Parser for Arcade data format"""
    
    def __init__(self, data: Dict[str, Any]):
        self.data = data
        self.captured_events = data.get('capturedEvents', [])
        self.steps = data.get('steps', [])
        self.name = data.get('name', 'Untitled Flow')
        self.description = data.get('description', '')
    
    def extract_user_interactions(self) -> List[str]:
        """Extract user interactions from capturedEvents and steps"""
        interactions = []
        
        # Process captured events
        for event in self.captured_events:
            interaction = self._parse_event(event)
            if interaction:
                interactions.append(interaction)
        
        # Process steps for additional context
        step_interactions = self._parse_steps()
        interactions.extend(step_interactions)
        
        return interactions
    
    def _parse_event(self, event: Dict[str, Any]) -> str:
        """Parse individual event into human-readable format"""
        event_type = event.get('type')
        
        if event_type == 'click':
            # Find corresponding step for more context
            click_id = event.get('clickId')
            step_context = self._find_step_by_click_id(click_id)
            
            if step_context:
                click_context = step_context.get('clickContext', {})
                text = click_context.get('text', '')
                element_type = click_context.get('elementType', '')
                
                if text and element_type:
                    return f"Clicked on {element_type}: '{text}'"
                elif text:
                    return f"Clicked on '{text}'"
                elif element_type:
                    return f"Clicked on {element_type}"
            
            return "Performed a click action"
        
        elif event_type == 'typing':
            duration = event.get('endTimeMs', 0) - event.get('startTimeMs', 0)
            return f"Typed text (duration: {duration}ms)"
        
        elif event_type == 'scrolling':
            duration = event.get('endTimeMs', 0) - event.get('startTimeMs', 0)
            return f"Scrolled page (duration: {duration}ms)"
        
        elif event_type == 'dragging':
            duration = event.get('endTimeMs', 0) - event.get('startTimeMs', 0)
            return f"Dragged element (duration: {duration}ms)"
        
        return f"Performed {event_type} action"
    
    def _find_step_by_click_id(self, click_id: str) -> Dict[str, Any]:
        """Find step data by click ID"""
        for step in self.steps:
            if step.get('id') == click_id:
                return step
        return {}
    
    def _parse_steps(self) -> List[str]:
        """Extract additional interactions from steps"""
        interactions = []
        
        for step in self.steps:
            step_type = step.get('type')
            
            if step_type == 'CHAPTER':
                title = step.get('title', '')
                if title:
                    interactions.append(f"Started chapter: '{title}'")
            
            elif step_type == 'IMAGE' and 'clickContext' in step:
                click_context = step.get('clickContext', {})
                text = click_context.get('text', '')
                element_type = click_context.get('elementType', '')
                page_url = step.get('pageContext', {}).get('url', '')
                
                # Extract domain for context
                domain = ''
                if page_url:
                    try:
                        from urllib.parse import urlparse
                        domain = urlparse(page_url).netloc
                    except:
                        pass
                
                context_parts = []
                if domain:
                    context_parts.append(f"on {domain}")
                if text and element_type:
                    context_parts.append(f"clicked {element_type} '{text}'")
                elif text:
                    context_parts.append(f"clicked '{text}'")
                elif element_type:
                    context_parts.append(f"clicked {element_type}")
                
                if context_parts:
                    interactions.append("Interacted " + " - ".join(context_parts))
        
        return interactions
    
    def generate_summary(self) -> str:
        """Generate human-friendly summary using OpenAI"""
        try:
            # Extract key information
            interactions = self.extract_user_interactions()
            flow_name = self.name or "Unknown Flow"
            page_contexts = self._extract_page_contexts()
            search_terms = self._extract_search_terms()
            
            # Format data for prompt
            website = page_contexts[0] if page_contexts else "Unknown website"
            search_terms_str = ', '.join(search_terms) if search_terms else "None"
            interactions_str = '\n'.join(f"- {interaction}" for interaction in interactions[:10])  # Limit to first 10 interactions
            
            # Use OpenAI to generate summary
            client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            
            prompt = SUMMARY_PROMPT.format(
                flow_name=flow_name,
                website=website,
                search_terms=search_terms_str,
                interactions=interactions_str
            )
            
            response = client.chat.completions.create(
                model="gpt-4",  # Using GPT-4 as GPT-5 may not be available yet
                messages=[
                    {"role": "system", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            # Fallback to original logic if OpenAI fails
            print(f"Warning: OpenAI summary generation failed ({str(e)}), using fallback method.")
            return self._generate_fallback_summary()
    
    def _generate_fallback_summary(self) -> str:
        """Fallback summary generation (original logic)"""
        interactions = self.extract_user_interactions()
        
        # Extract key information
        flow_name = self.name
        page_contexts = self._extract_page_contexts()
        search_terms = self._extract_search_terms()
        
        # Build summary
        summary_parts = []
        
        # Add flow context
        if flow_name and flow_name != 'Untitled Flow':
            summary_parts.append(f"User completed a flow titled '{flow_name}'.")
        
        # Add website context
        if page_contexts:
            main_site = page_contexts[0] if page_contexts else None
            if main_site:
                summary_parts.append(f"The session took place on {main_site}.")
        
        # Add search context
        if search_terms:
            summary_parts.append(f"User searched for: {', '.join(search_terms)}.")
        
        # Add interaction summary
        if interactions:
            key_actions = self._identify_key_actions(interactions)
            if key_actions:
                summary_parts.append(f"Key actions included: {', '.join(key_actions)}.")
        
        # Add goal inference
        goal = self._infer_user_goal()
        if goal:
            summary_parts.append(f"The user's goal appears to be: {goal}")
        
        return " ".join(summary_parts)
    
    def generate_social_media_image(self, output_path: str = "social_media_promotion.png") -> str:
        """Generate a social media promotional image using DALL-E"""
        try:
            # Extract product information from interactions
            interactions = self.extract_user_interactions()
            page_contexts = self._extract_page_contexts()
            search_terms = self._extract_search_terms()
            
            # Identify primary product from interactions
            primary_product = self._extract_primary_product(interactions, search_terms)
            product_details = self._extract_product_details(interactions)
            website_name = page_contexts[0] if page_contexts else "Target"
            product_category = self._infer_product_category(primary_product, search_terms)
            
            # Generate specific promotional text phrases
            promotional_text = self._generate_promotional_text(primary_product, product_details, website_name)
            
            # Create clean product image prompt (no text)
            prompt = self._create_clean_product_prompt(
                primary_product, product_details, website_name, product_category
            )
            
            print("🎨 Generating clean product image...")
            
            # Use gpt-image-1 with integrated text
            model = "gpt-image-1"
            prompt = self._create_prompt_with_text(prompt, promotional_text)
            print("🎨 Generating image with integrated text using gpt-image-1...")
            
            # Generate product image
            client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            
            # Set quality parameter for gpt-image-1
            quality = "high"  # gpt-image-1 uses: low, medium, high, auto
            
            response = client.images.generate(
                model=model,
                prompt=prompt,
                size="1024x1024",
                quality=quality,
                n=1,
            )
            
            # gpt-image-1 returns base64 encoded image directly
            if hasattr(response.data[0], 'b64_json') and response.data[0].b64_json:
                import base64
                image_data = base64.b64decode(response.data[0].b64_json)
                
                # Save the image directly from base64 data
                with open(output_path, 'wb') as f:
                    f.write(image_data)
                print(f"✅ gpt-image-1 image saved successfully to {output_path}")
            else:
                raise Exception(f"gpt-image-1 returned unexpected response format: {response}")
            
            print(f"✅ Social media image with integrated text saved as: {output_path}")
            print(f"📝 Generated with promotional text:")
            print(f"   Discount: {promotional_text['discount']}")
            print(f"   Product: {promotional_text['product_name']}")
            print(f"   Urgency: {promotional_text['urgency']}")
            print(f"   CTA: {promotional_text['cta']}")
            print(f"   Tagline: {promotional_text['tagline1']}")
            print(f"   Extra: {promotional_text['tagline2']}")
            print(f"   Brand: {promotional_text['website']}")
            
            return output_path
                
        except Exception as e:
            print(f"❌ Image generation failed: {str(e)}")
            return ""
    
    def _extract_primary_product(self, interactions: List[str], search_terms: List[str]) -> str:
        """Extract the main product from interactions and search terms"""
        # Look for product names in interactions
        for interaction in interactions:
            if "razor" in interaction.lower() and "scooter" in interaction.lower():
                return "Razor A5 Lux 2 Wheel Kick Scooter"
            elif "scooter" in interaction.lower():
                return "Kick Scooter"
        
        # Fallback to search terms
        if search_terms:
            return search_terms[0].title()
        
        # Default fallback
        return "Featured Product"
    
    def _extract_product_details(self, interactions: List[str]) -> str:
        """Extract specific product details like color, variant, etc."""
        details = []
        
        for interaction in interactions:
            if "blue" in interaction.lower():
                details.append("Blue")
            elif "pink" in interaction.lower():
                details.append("Pink")
            elif "red" in interaction.lower():
                details.append("Red")
        
        if details:
            return f"Available in {', '.join(details)}"
        
        return "Multiple colors available"
    
    def _infer_product_category(self, primary_product: str, search_terms: List[str]) -> str:
        """Infer the product category for targeting"""
        product_lower = primary_product.lower()
        
        if "scooter" in product_lower:
            return "outdoor sports and recreation"
        elif "bike" in product_lower or "bicycle" in product_lower:
            return "cycling and fitness"
        elif "toy" in product_lower:
            return "toys and games"
        elif search_terms and "electronics" in ' '.join(search_terms).lower():
            return "consumer electronics"
        
        return "lifestyle products"
    
    def _generate_promotional_text(self, primary_product: str, product_details: str, website_name: str) -> Dict[str, str]:
        """Generate specific promotional text phrases to avoid DALL-E text generation issues"""
        # Extract discount percentage (15-25% range for realism)
        import random
        discount = random.choice([15, 20, 25])
        
        # Generate product-specific phrases
        product_name = primary_product.replace("Razor A5 Lux 2 Wheel Kick", "Razor A5").replace("Scooter", "Scooter")
        if len(product_name) > 15:
            product_name = "Razor Scooter"
        
        # Create specific text elements
        promotional_text = {
            "discount": f"{discount}% OFF",
            "product_name": product_name,
            "urgency": random.choice(["Today Only", "Limited Time", "Flash Sale"]),
            "cta": random.choice(["Shop Now", "Get Yours", "Buy Today"]),
            "tagline1": self._get_product_tagline(primary_product, product_details),
            "tagline2": random.choice(["Free Shipping", "Best Price", "Top Rated"]),
            "website": website_name.upper() if website_name.lower() != "www.target.com" else "TARGET"
        }
        
        return promotional_text
    
    def _get_product_tagline(self, primary_product: str, product_details: str) -> str:
        """Generate product-specific taglines"""
        if "scooter" in primary_product.lower():
            if "blue" in product_details.lower() and "pink" in product_details.lower():
                return "Blue or Pink"
            elif "blue" in product_details.lower():
                return "Cool Blue"
            elif "pink" in product_details.lower():
                return "Pretty Pink"
            else:
                return "Ride in Style"
        elif "bike" in primary_product.lower():
            return "Cycle Smart"
        else:
            return "Great Deal"
    
    def _create_clean_product_prompt(self, primary_product: str, product_details: str, 
                                   website_name: str, product_category: str) -> str:
        """Create a prompt for a clean product image using external prompt template"""
        
        # Get the image generation prompt from external file
        template = PROMPTS.get('IMAGE_GENERATION_PROMPT', 
                              'Create a vibrant, professional product showcase image for {primary_product}.')
        
        # Format the template with actual values
        prompt = template.format(
            primary_product=primary_product,
            product_details=product_details,
            website_name=website_name,
            product_category=product_category
        )

        return prompt
    
    def _create_prompt_with_text(self, base_prompt: str, promotional_text: Dict[str, str]) -> str:
        """Enhance the base prompt to include promotional text when using GPT-image-1"""
        text_elements = []
        
        # Add discount text if available
        if promotional_text.get('discount'):
            text_elements.append(f"'{promotional_text['discount']}'")
        
        # Add urgency/badge text
        if promotional_text.get('urgency'):
            text_elements.append(f"'{promotional_text['urgency']}'")
        
        # Add CTA text
        if promotional_text.get('cta'):
            text_elements.append(f"'{promotional_text['cta']}'")
        
        # Add product name prominently
        if promotional_text.get('product_name'):
            text_elements.append(f"'{promotional_text['product_name']}'")
        
        # Add taglines
        if promotional_text.get('tagline1'):
            text_elements.append(f"'{promotional_text['tagline1']}'")
        
        # Add website/brand
        if promotional_text.get('website'):
            text_elements.append(f"'{promotional_text['website']}'")
        
        if text_elements:
            text_instruction = f" Include the following promotional text elements prominently and stylishly overlaid on the image: {', '.join(text_elements)}. Make the text highly readable with good contrast, professional typography, and attractive placement that doesn't obscure the main product."
            return base_prompt + text_instruction
        
        return base_prompt
    
    def _extract_page_contexts(self) -> List[str]:
        """Extract unique page contexts/domains"""
        domains = set()
        
        for step in self.steps:
            page_context = step.get('pageContext', {})
            url = page_context.get('url', '')
            
            if url:
                try:
                    from urllib.parse import urlparse
                    domain = urlparse(url).netloc
                    if domain:
                        domains.add(domain)
                except:
                    pass
        
        return list(domains)
    
    def _extract_search_terms(self) -> List[str]:
        """Extract search terms from URLs and contexts"""
        search_terms = []
        
        for step in self.steps:
            page_context = step.get('pageContext', {})
            url = page_context.get('url', '')
            
            # Look for search terms in URL
            if 'searchTerm=' in url:
                try:
                    from urllib.parse import parse_qs, urlparse
                    parsed = urlparse(url)
                    params = parse_qs(parsed.query)
                    search_term = params.get('searchTerm', [])
                    if search_term:
                        search_terms.extend(search_term)
                except:
                    pass
        
        return search_terms
    
    def _identify_key_actions(self, interactions: List[str]) -> List[str]:
        """Identify the most important actions from the interaction list"""
        key_actions = []
        
        for interaction in interactions:
            # Look for important action keywords
            if any(keyword in interaction.lower() for keyword in [
                'search', 'add to cart', 'checkout', 'purchase', 'buy',
                'login', 'sign up', 'register', 'submit'
            ]):
                key_actions.append(interaction.lower())
        
        # If no key actions found, take first few actions
        if not key_actions and interactions:
            key_actions = [interactions[0].lower()]
            if len(interactions) > 1:
                key_actions.append(interactions[-1].lower())
        
        return key_actions
    
    def _infer_user_goal(self) -> str:
        """Infer the user's goal based on the flow name and actions"""
        flow_name = self.name.lower()
        
        # Common goal patterns
        if 'cart' in flow_name or 'add to cart' in flow_name:
            return "adding items to their shopping cart"
        elif 'checkout' in flow_name or 'purchase' in flow_name:
            return "completing a purchase"
        elif 'search' in flow_name:
            return "finding specific products or information"
        elif 'register' in flow_name or 'sign up' in flow_name:
            return "creating a new account"
        elif 'login' in flow_name or 'sign in' in flow_name:
            return "accessing their account"
        
        # Extract from flow name if it's descriptive
        if self.name and self.name != 'Untitled Flow':
            return f"completing the task: {self.name}"
        
        return "navigating and interacting with the website"


def parse_arcade_data(json_data: str, generate_image: bool = False) -> Dict[str, Any]:
    """Main function to parse Arcade data and return results"""
    try:
        # Parse JSON
        data = json.loads(json_data)
        
        # Create parser
        parser = ArcadeParser(data)
        
        # Extract results
        interactions = parser.extract_user_interactions()
        summary = parser.generate_summary()
        
        result = {
            'user_interactions': interactions,
            'summary': summary,
            'flow_name': parser.name,
            'total_events': len(parser.captured_events),
            'total_steps': len(parser.steps)
        }
        
        # Generate social media image if requested
        if generate_image:
            image_path = parser.generate_social_media_image()
            result['social_media_image'] = image_path
        
        return result
    
    except json.JSONDecodeError as e:
        return {
            'error': f"JSON parsing error: {str(e)}",
            'user_interactions': [],
            'summary': ''
        }
    except Exception as e:
        return {
            'error': f"Processing error: {str(e)}",
            'user_interactions': [],
            'summary': ''
        }


if __name__ == "__main__":
    # Example usage with the provided data
    example_data = '''{ "createdBy": "abcde123456", "externalName": null, "description": "", "schemaVersion": "1.1.0", "cta": {}, "editors": [], "optimizeFlowForMobileView": true, "folderId": null, "themeId": null, "menu": null, "showCaptions": true, "teamId": "6cleoKGEaAz9hBaGgDGG", "showFlowNavIndicator": "AUTO", "flowWrapper": 1, "customCursor": 1, "font": "Inter", "showStartOverlay": false, "showBackNextButtons": false, "startOverlayButtonText": "", "autoplay": { "enabled": false, "delay": null }, "backgroundMusicUrl": null, "backgroundMusicVolume": 1, "sharePageLayout": { "type": "arcade-only", "showHeader": true, "showLogo": true, "showButton": true }, "useVersioning": false, "createdWith": "extension/1.5.9", "uploadId": "2RnSqfsV4EsODmUiPKoW", "hasUsedAI": true, "created": { "_seconds": 1756746380, "_nanoseconds": 124000000 }, "capturedEvents": [ { "type": "click", "clickId": "c5303a58-fa0b-4758-ba5d-e6b3871b1db2", "frameX": 1032.79296875, "frameY": 81.30859375, "timeMs": 1756746383245, "tabId": 471877758, "frameId": 0 }, { "type": "typing", "startTimeMs": 1756746383857, "endTimeMs": 1756746384842, "tabId": 471877758, "frameId": 0 }, { "type": "scrolling", "startTimeMs": 1756746386145, "endTimeMs": 1756746391996, "tabId": 471877758, "frameId": 0 }, { "type": "click", "clickId": "7c65bef7-9d8a-4c64-8c19-4300b535ee48", "frameX": 749.2578125, "frameY": 276.70703125, "timeMs": 1756746392812, "tabId": 471877758, "frameId": 0 }, { "type": "scrolling", "startTimeMs": 1756746393039, "endTimeMs": 1756746394535, "tabId": 471877758, "frameId": 0 }, { "type": "click", "clickId": "07a2f271-1154-47d3-afc1-50171e8b7774", "frameX": 894.50390625, "frameY": 346.33203125, "timeMs": 1756746395965, "tabId": 471877758, "frameId": 0 }, { "type": "click", "clickId": "35a736c7-0838-464c-9d31-5a859c805dad", "frameX": 950.42578125, "frameY": 368.1484375, "timeMs": 1756746397372, "tabId": 471877758, "frameId": 0 }, { "type": "click", "clickId": "cdbacdd2-5e52-491e-976a-15b67029ac75", "frameX": 1154.27734375, "frameY": 628.66015625, "timeMs": 1756746398706, "tabId": 471877758, "frameId": 0 }, { "type": "click", "clickId": "5d89468d-eb60-4583-8b0f-098561a17421", "frameX": 1584.890625, "frameY": 1756746401153, "tabId": 471877758, "frameId": 0 }, { "type": "click", "clickId": "3d7a3fe4-f028-4042-97e9-0570449b5ade", "frameX": 1509.85546875, "frameY": 35.60546875, "timeMs": 1756746403393, "tabId": 471877758, "frameId": 0 }, { "type": "dragging", "startTimeMs": 1756746403399, "endTimeMs": 1756746403513, "tabId": 471877758, "frameId": 0 } ], "ai": { "recordingEndRequestId": "aeeb1f54-8d30-4972-b8ad-f8ad858cd398", "recordingEndVersionId": "a08eadc9-8a1c-4522-b2b8-31f9491df330" }, "aspectRatio": 0.4880046811000585, "status": 1, "processedAIReason": "Success", "useCase": "promotional", "name": "Add a Scooter to Your Cart on Target.com", "steps": [ { "type": "CHAPTER", "id": "8fe5c5d9-8ca0-418d-8e74-b54f17cfc996", "title": "Add a Scooter to Your Cart on Target.com", "subtitle": "Learn how to browse, customize, and add a Razor scooter to your Target cart for easy checkout.", "theme": "light", "textAlign": "left", "showPreviewImage": true, "showLogo": false, "paths": [ { "id": "8c3bdd70-8d4e-444f-8daa-0e5263f6f3f6", "buttonText": "Get Started", "buttonColor": "#2142e7", "buttonTextColor": "#fdfdff", "pathType": "step" } ] }, { "id": "c5303a58-fa0b-4758-ba5d-e6b3871b1db2", "type": "IMAGE", "url": "https://cdn.arcade.software/extension-uploads/2RnSqfsV4EsODmUiPKoW/image/e2a8f5fa-19e8-4832-82cc-76e76f65b0b3.png", "originalImageUrl": "https://cdn.arcade.software/extension-uploads/2RnSqfsV4EsODmUiPKoW/image/e2a8f5fa-19e8-4832-82cc-76e76f65b0b3.png", "blurhash": "UWQSrGog_Nxs^0aNE2ouM|jra0WFRpadr;kE", "hasHTML": true, "size": { "height": 1668, "width": 3418 }, "hotspots": [ { "id": "ae063208-ffb7-4ca7-a158-a8c66fea097c", "width": 40, "height": 40, "label": "Tap the search bar to start looking for your next favorite product.", "style": "pulsating", "defaultOpen": true, "textColor": "#fdfdff", "bgColor": "#2142e7", "x": 0.6043259033060269, "y": 0.09749231864508394 } ], "pageContext": { "url": "https://www.target.com/", "title": "Target : Expect More. Pay Less.", "description": "Shop Target online and in-store for everything from groceries and essentials to clothing and electronics. Choose contactless pickup or delivery today.", "width": 1709, "height": 834, "language": "en-US" }, "clickContext": { "cssSelector": "input[id=\\"search\\"]", "text": "search", "elementType": "other", "sections": [ "Footer" ], "originalRect": { "x": 829, "y": 68, "width": 472, "height": 44 } }, "assetId": "c5303a58-fa0b-4758-ba5d-e6b3871b1db2" } ] }'''
    
    result = parse_arcade_data(example_data)
    
    print("=== ARCADE DATA ANALYSIS ===\n")
    print(f"Flow Name: {result.get('flow_name', 'Unknown')}")
    print(f"Total Events: {result.get('total_events', 0)}")
    print(f"Total Steps: {result.get('total_steps', 0)}")
    print()
    
    print("=== USER INTERACTIONS ===")
    for i, interaction in enumerate(result.get('user_interactions', []), 1):
        print(f"{i}. {interaction}")
    print()
    
    print("=== SUMMARY ===")
    print(result.get('summary', 'No summary available'))
    
    if 'error' in result:
        print(f"\n=== ERROR ===")
        print(result['error'])
