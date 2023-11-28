# Jira Issue Creator

This project provides scripts to automate the creation of Jira issues and their respective sub-tasks using data from CSV
files.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## Features

- Read data from CSV files to extract Jira issue details.
- Automated creation of Jira issues.
- Automated creation of sub-tasks linked to the main issues.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/star7js/jira-upload-csv.git

2. Navigate to the project directory:
   cd jira-upload-csv

3. Install the required dependencies:
   pip install -r requirements.txt

## Usage

1. Update the Jira authentication details in the respective script.
2. Place your CSV files in the `data/` directory.
3. Run the script:
   python src/script_name.py

## Project Structure

project_name/
│
├── README.md            
├── requirements.txt     
│
├── src/                 
│ ├── script1.py       
│ ├── script2.py       
│ └── ...              
│
├── tests/               
│ ├── test_script1.py  
│ ├── test_script2.py  
│ └── ...              
│
└── data/                
├── data1.csv
└── ...

## Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you'd like to change.

## License

This project is licensed under the MIT License. See `LICENSE` file for details.
