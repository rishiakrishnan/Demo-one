import yaml
from jinja2 import Environment, FileSystemLoader

def load_yaml(file_path):
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)
        if isinstance(data, set):
            raise ValueError("YAML file contains a set, which is not supported")
        return data

def file_input(src_temp, path_name, temp_name, file_name, typ):
    try:
        # Load the input data from the YAML file
        input_data = load_yaml(f'yaml/input_detail.yaml')

        # Load the Jinja2 environment and templates
        env = Environment(loader=FileSystemLoader(src_temp))
        template = env.get_template(f'{temp_name}.j2')

        # Render the template with the input data
        output = template.render(input_data)

        # Write the output to the file
        with open(f'{path_name}/{file_name}.{typ}', 'w') as file:
            file.write(output)
    except Exception as e:
        print(f"Error generating file for {file_name}: {e}")

if __name__ == "__main__":
    print("executing")

    pinmux_files = [
        ("templates/pinmux", "pinmux/test", "pinmap", "pinmap", "txt"),
    ]

    sos_files = [
        ("templates", "../sos", "DebugSoc", "DebugSoc", "bsv"),
        ("templates", "../sos", "mixed_cluster", "mixed_cluster", "bsv"),
        ("templates", "../sos", "pinmux_axi4lite", "pinmux_axi4lite", "bsv"),
        ("templates", "../sos", "pwm_cluster", "pwm_cluster", "bsv"),
        ("templates", "../sos", "sign_dump", "sign_dump", "bsv"),
        ("templates", "../sos", "Soc", "Soc", "bsv"),
        ("templates", "../sos", "spi_cluster", "spi_cluster", "bsv"),
        ("templates", "../sos", "TbSoc", "TbSoc", "bsv"),
        ("templates", "../sos", "uart_cluster", "uart_cluster", "bsv"),
        ("templates", "../sos", "dsoc", "Soc", "defines"),
        ("templates", "../sos", "io_func", "io_func", "bsv"),
    ]

    arty_a7_files = [
    ("templates/boards/arty_a7", "../sos/boards/arty_a7", "DebugSoc", "DebugSoc", "bsv"),
    ("templates/boards/arty_a7", "../sos/boards/arty_a7", "dsoc", "Soc", "defines"),
    ("templates/boards/arty_a7", "../sos/boards/arty_a7", "mixed_cluster", "mixed_cluster", "bsv"),
    ("templates/boards/arty_a7", "../sos/boards/arty_a7", "pinmux_axi4lite", "pinmux_axi4lite", "bsv"),
    ("templates/boards/arty_a7", "../sos/boards/arty_a7", "pwm_cluster", "pwm_cluster", "bsv"),
    ("templates/boards/arty_a7", "../sos/boards/arty_a7", "Soc", "Soc", "bsv"),
    ("templates/boards/arty_a7", "../sos/boards/arty_a7", "spi_cluster", "spi_cluster", "bsv"),
    ("templates/boards/arty_a7", "../sos/boards/arty_a7", "uart_cluster", "uart_cluster", "bsv"),
]


    # Generate pinmux-related files
    for src_temp, path_name, temp_name, file_name, typ in pinmux_files:
        file_input(src_temp, path_name, temp_name, file_name, typ)

    print("PINMUX REQUIREMENT CORRECTION DONE..")

    # Generate common required files and store them in the 'sos' directory
    for src_temp, path_name, temp_name, file_name, typ in sos_files:
        file_input(src_temp, path_name, temp_name, file_name, typ)

    for src_temp, path_name, temp_name, file_name, typ in arty_a7_files:
        file_input(src_temp, path_name, temp_name, file_name, typ)

    print("COMMON REQUIRED FILES ARE GENERATED..")

    print("PINMUX EXECUTION NEXT..")
