#!/usr/bin/env python3
"""
Command-line interface for analyzing Arcade data

Usage:
    python analyze_arcade.py <json_file> [--generate-image]
    python analyze_arcade.py example_data.json
    python analyze_arcade.py example_data.json --generate-image
"""

import sys
import json
from arcade_parser import parse_arcade_data


def main():
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python analyze_arcade.py <json_file> [--generate-image]")
        print("Example: python analyze_arcade.py example_data.json")
        print("Example: python analyze_arcade.py example_data.json --generate-image")
        sys.exit(1)
    
    json_file = sys.argv[1]
    generate_image = len(sys.argv) == 3 and sys.argv[2] == "--generate-image"
    
    try:
        # Read JSON file
        with open(json_file, 'r', encoding='utf-8') as f:
            json_data = f.read()
        
        # Parse the data
        result = parse_arcade_data(json_data, generate_image=generate_image)
        
        # Display results
        print("=" * 60)
        print("ARCADE DATA ANALYSIS")
        print("=" * 60)
        print()
        
        if 'error' in result:
            print(f"❌ ERROR: {result['error']}")
            sys.exit(1)
        
        # Basic info
        print(f"📊 Flow Name: {result.get('flow_name', 'Unknown')}")
        print(f"📈 Total Events: {result.get('total_events', 0)}")
        print(f"📋 Total Steps: {result.get('total_steps', 0)}")
        print()
        
        # User interactions
        print("🎯 USER INTERACTIONS:")
        print("-" * 40)
        interactions = result.get('user_interactions', [])
        if interactions:
            for i, interaction in enumerate(interactions, 1):
                print(f"{i:2d}. {interaction}")
        else:
            print("No interactions found.")
        print()
        
        # Summary
        print("📝 HUMAN-FRIENDLY SUMMARY:")
        print("-" * 40)
        summary = result.get('summary', 'No summary available')
        print(summary)
        print()
        
        # Show image generation result if requested
        if generate_image and 'social_media_image' in result:
            image_path = result['social_media_image']
            if image_path:
                print("🎨 SOCIAL MEDIA IMAGE:")
                print("-" * 40)
                print(f"Generated promotional image: {image_path}")
                print()
        
        print("✅ Analysis completed successfully!")
        
    except FileNotFoundError:
        print(f"❌ Error: File '{json_file}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
