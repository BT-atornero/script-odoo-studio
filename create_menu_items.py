import xml.etree.ElementTree as ET
import os


def transform_menu_xml(input_path, output_path, header):
    # Load the input XML
    tree = ET.parse(input_path)
    root = tree.getroot()

    # Create the root element for the output XML
    output_root = ET.Element("odoo")

    # Process each record in the input XML
    for record in root.findall("record"):
        if record.get("model") != "ir.ui.menu":
            continue

        # Prepare to collect the attributes for the <menuitem>
        menuitem_attributes = {}

        # Assign attributes to the menuitem based on fields in the record
        menuitem_attributes["id"] = record.get("id")

        for field in record.findall("field"):
            field_name = field.get("name")
            field_value = field.text.strip() if field.text else ""

            if field_name == "name" and field_value:  # Only add if the field is not empty
                menuitem_attributes["name"] = field_value
            elif field_name == "parent_id" and field.get("ref"):
                parent_ref = field.get("ref")
                if parent_ref:  # Only add if the parent reference is not empty
                    menuitem_attributes["parent"] = parent_ref
            elif field_name == "sequence" and field_value:  # Only add if the field is not empty
                menuitem_attributes["sequence"] = field_value
            elif field_name == "groups_id":
                # Convert the list of groups into a string format
                groups = field.get("eval")
                if groups:  # Only add if groups are not empty
                    groups = groups.replace("[(6, 0, [", "").replace("])]", "").replace("ref(", "").replace(")", "")
                    groups = groups.replace("'", "").replace(" ", "")
                    if groups:  # Check if groups string is not empty
                        menuitem_attributes["groups"] = groups
            elif field_name == "action" and field.get("ref"):
                action_ref = field.get("ref")
                if action_ref:
                    menuitem_attributes["action"] = action_ref

        # Only add the menuitem if it has at least one attribute
        if menuitem_attributes:
            # Create the menuitem string with aligned attributes
            menuitem_str = "    <menuitem"
            max_key_length = max(len(key) for key in menuitem_attributes.keys())
            for key, value in menuitem_attributes.items():
                # Properly format the value to handle spaces and wrap it in quotes
                menuitem_str += f'\n        {key}="{value}"'
            menuitem_str += ' />\n'  # Close the menuitem and add a blank line

            # Append the formatted menuitem string to the output root
            output_root.append(ET.Element("dummy"))  # Placeholder to append later

            # Store the string representation for final output
            output_root[-1].tag = 'menuitem'  # Change the placeholder to the desired tag
            output_root[-1].text = menuitem_str  # Assign the formatted string

    # Prepare final XML with header and a single <odoo> element
    final_xml = f"<?xml version='1.0' encoding='utf-8'?>\n{header}\n<odoo>\n"

    # Append each menuitem text to final XML
    for item in output_root:
        final_xml += item.text

    final_xml += "</odoo>"

    # Save the XML to the output file
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(final_xml)
        f.write("\n")  # Add a blank line at the end

    print(f"The transformed file has been saved to '{output_path}'.")


# Example usage
input_path = "input/ir_ui_menu.xml"  # Path to the input XML file
output_path = "views/menu.xml"  # Path to the output XML file

# Ensure the output directory exists
os.makedirs(os.path.dirname(output_path), exist_ok=True)

header = "<!-- This file was generated automatically -->"  # Example header

transform_menu_xml(input_path, output_path, header)
