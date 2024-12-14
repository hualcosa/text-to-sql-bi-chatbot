# BI Chatbot (Text to SQL)

This project is a Business Intelligence (BI) Chatbot that uses natural language processing to generate SQL queries, execute them against a database, and visualize the results. It's designed to work with an NBA dataset and uses Amazon Bedrock for AI capabilities.

## Project Structure

The project is organized as follows:

- `notebooks/`: Jupyter notebooks for exploratory data analysis and development
- `utilities/`: Python modules containing utility functions
- `app.py`: Main Streamlit application
- `requirements.txt`: List of Python dependencies

## Key Components

1. **SQL Query Generation**: The chatbot converts natural language questions into SQL queries using AI models.

2. **Database Interaction**: Executes SQL queries against a Redshift database containing NBA data.

3. **Data Visualization**: Generates Python code to visualize query results using libraries like Plotly and Streamlit.

4. **LangGraph Integration**: Uses LangGraph to create a workflow for processing user queries, generating SQL, and creating visualizations.

## Setup and Installation

1. Clone the repository:
   ```
   git clone https://github.com/hualcosa/text-to-sql-bi-chatbot.git
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up your AWS credentials and configure access to Amazon Bedrock and Redshift.

4. Update the `config/config.json` file with your Redshift cluster details.

## Running the Application

To run the Streamlit application:
```
streamlit run app.py
```

## Key Features

- Natural language to SQL query conversion
- Automatic SQL query correction and refinement
- Data visualization generation
- Interactive chat interface

## Future Enhancements

- Implement more sophisticated context extraction for better query understanding
- Enhance visualization capabilities with more chart types and options
- Improve error handling and user feedback mechanisms

## Contributing

Contributions to this project are welcome. Please follow these steps:

1. Fork the repository
2. Create a new branch for your feature
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request


## License

This project is licensed under the MIT License.

MIT License

Copyright (c) 2024 Amazon Web Services

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Acknowledgments

This project uses various open-source libraries and AWS services. We thank all the contributors and maintainers of these tools.
