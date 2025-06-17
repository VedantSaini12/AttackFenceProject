# AttackFence Employee Rating Platform

## Download and run on your own computer
The project is made in streamlit, and some basic steps need to be initialised before it can work on your computer.
1. **Setup Environment**: Ensure you have Python installed on your system. It's recommended to use a virtual environment for Python projects to manage dependencies effectively. To setup your own venv, type the following:
- ```
  python -m venv .venv
  ```
- After that, start using your virtual environment as your development environment as follows:
  ```
  .venv\Scripts\activate.bat
  ```
#### Note: This is for Windows CMD and it may differ for zshell and bash users. Kindly refer to [Streamlit Integration Docs](https://docs.streamlit.io/get-started/installation) for your specific OS.

2. **Install Dependencies**:
   - Install the required Python packages by running:
     ```
     pip install streamlit bcrypt mysql-connector-python
     ```
   
3. **Launch the App**:
   - Run the app using Streamlit by executing:
     ```
     streamlit run ./Home.py
     ```
   - Streamlit will start the web server, and you can access the app through the web browser at the indicated URL (usually `http://localhost:8501`)."# AttackFenceProject" 
