import xml.etree.ElementTree as ET
import os

def transform_model_access_xml(input_path, output_path):
    # Load the input XML
    tree = ET.parse(input_path)
    root = tree.getroot()

    # Open the output CSV file
    with open(output_path, "w", encoding="utf-8") as csv_file:
        # Write the header line
        csv_file.write("id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink\n")

        # Process each record in the input XML
        for record in root.findall("record"):
            if record.get("model") != "ir.model.access":
                continue

            # Prepare to collect the fields for the CSV line
            csv_line = []

            # Add the record id
            csv_line.append(record.get("id"))

            # Iterate over fields to extract relevant data
            perm_read = perm_write = perm_create = perm_unlink = "0"
            for field in record.findall("field"):
                field_name = field.get("name")
                field_value = field.text.strip() if field.text else ""

                if field_name == "name":
                    name = field_value
                elif field_name == "model_id" and field.get("ref"):
                    model = field.get("ref")
                elif field_name == "group_id" and field.get("ref"):
                    group = field.get("ref")
                elif field_name == "perm_read":
                    perm_read = "1" if field.get("eval") == "True" else "0"
                elif field_name == "perm_write":
                    perm_write = "1" if field.get("eval") == "True" else "0"
                elif field_name == "perm_create":
                    perm_create = "1" if field.get("eval") == "True" else "0"
                elif field_name == "perm_unlink":
                    perm_unlink = "1" if field.get("eval") == "True" else "0"
            csv_line.append(name)
            csv_line.append(model)
            csv_line.append(group)
            csv_line.append(perm_read)
            csv_line.append(perm_write)
            csv_line.append(perm_create)
            csv_line.append(perm_unlink)
            # Join the CSV line with commas and write to the file
            csv_file.write(",".join(csv_line) + "\n")

    print(f"The model access CSV file has been saved to '{output_path}'.")

# Example usage
input_path = "input/ir_model_access.xml"  # Path to the input XML file
output_path = "security/ir.model.access.csv"  # Path to the output CSV file

# Ensure the output directory exists
os.makedirs(os.path.dirname(output_path), exist_ok=True)

transform_model_access_xml(input_path, output_path)
