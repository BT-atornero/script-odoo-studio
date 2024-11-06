import xml.etree.ElementTree as ET
import xml.dom.minidom
import os


def order_and_split_by_model(view_xml_path, action_xml_path, view_order, action_order, view_fields_to_remove,
                             action_fields_to_remove, header):
    # Create output folder if it doesn't exist
    output_folder = 'views'
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    def process_records(xml_path, model_type, order, fields_to_remove):
        tree = ET.parse(xml_path)
        root = tree.getroot()

        # Ensure the file is wrapped in <odoo>
        if root.tag != 'odoo':
            raise ValueError("The XML file must be wrapped in an <odoo> element")

        records_by_model = {}

        for record in root.findall('record'):
            if record.get('model') != model_type:
                continue

            model_name_field = record.find('field[@name="model"]') if model_type == 'ir.ui.view' else record.find(
                'field[@name="res_model"]')
            if model_name_field is None:
                continue
            model_name = model_name_field.text.replace('.', '_')

            # Get all <field> within the <record> and apply ordering and filtering
            fields = record.findall('field')
            fields = [field for field in fields if field.get('name') not in fields_to_remove]
            fields.sort(key=lambda field: order.index(field.get('name')) if field.get('name') in order else len(order))

            # Clear existing <field> and add ordered (and filtered) fields
            for field in record.findall('field'):
                record.remove(field)
            for field in fields:
                record.append(field)

            # Add the <record> to the appropriate model group
            if model_name not in records_by_model:
                records_by_model[model_name] = []
            records_by_model[model_name].append(record)

        return records_by_model

    # Process views and actions separately
    view_records = process_records(view_xml_path, 'ir.ui.view', view_order, view_fields_to_remove)
    action_records = process_records(action_xml_path, 'ir.actions.act_window', action_order, action_fields_to_remove)

    # Merge the dictionaries
    all_records_by_model = {}
    for model_name, records in view_records.items():
        if model_name not in all_records_by_model:
            all_records_by_model[model_name] = {'views': [], 'act_windows': []}
        all_records_by_model[model_name]['views'].extend(records)
    for model_name, records in action_records.items():
        if model_name not in all_records_by_model:
            all_records_by_model[model_name] = {'views': [], 'act_windows': []}
        all_records_by_model[model_name]['act_windows'].extend(records)

    # Create separate XML files for each model value
    for model_name, record_groups in all_records_by_model.items():
        # Create the file for the current model
        model_file_path = os.path.join(output_folder, f"{model_name}_views.xml")
        model_root = ET.Element("odoo")

        # Add all views first, then act_windows for the current model
        for record in record_groups['views'] + record_groups['act_windows']:
            model_root.append(record)

        # Convert the XML to a string
        rough_string = ET.tostring(model_root, encoding='utf-8')
        dom = xml.dom.minidom.parseString(rough_string)

        # Use toprettyxml and then clean up the output to remove empty lines
        pretty_xml_as_string = dom.toprettyxml(indent="    ")  # 4-space indentation
        lines = pretty_xml_as_string.splitlines()

        # Remove the first line which contains the XML declaration
        cleaned_lines = [line for line in lines[1:] if line.strip()]  # Skip the first line and remove empty lines

        # Insert a blank line between each <record> block
        spaced_lines = []
        for line in cleaned_lines:
            spaced_lines.append(line)
            if "</record>" in line:
                spaced_lines.append("")  # Add a blank line after each </record>

        # Prepare final XML with header
        final_xml = "\n".join(spaced_lines)
        final_xml = f"<?xml version='1.0' encoding='utf-8'?>\n{header}\n{final_xml}\n"  # Add newline at the end

        # Save the file with the formatted structure
        with open(model_file_path, 'w', encoding='utf-8') as f:
            f.write(final_xml)

    print(f"Files generated in the '{output_folder}' folder with 4-space indentation.")


# Example usage
view_xml_path = 'input/ir_ui_view.xml'  # Path to the input XML file for ir.ui.view records
action_xml_path = 'input/ir_actions_act_window.xml'  # Path to the input XML file for ir.actions.act_window records

# Desired order and fields to remove for ir.ui.view records
view_order = ['name', 'model', 'inherit_id', 'priority', 'groups_id', 'arch']
view_fields_to_remove = ['mode', 'type', 'key', 'active', 'groups_id']

# Desired order and fields to remove for ir.actions.act_window records
action_order = ['name', 'res_model', 'view_mode', 'domain', 'filter', 'context', 'target', 'help']
action_fields_to_remove = ['view_id', 'binding_model_id', 'search_view_id', 'binding_view_types', 'binding_type',
                           'type', 'limit', 'usage', 'groups_id']

header = ("<!--\n"
          "Copyright (c) 2024 braintec AG (https://braintec.com)\n"
          "All Rights Reserved\n"
          "Licensed under the Odoo Proprietary License v1.0 (OPL).\n"
          "See LICENSE file for full licensing details.\n"
          "-->")  # Header text to add to each file

order_and_split_by_model(view_xml_path, action_xml_path, view_order, action_order, view_fields_to_remove,
                         action_fields_to_remove, header)
